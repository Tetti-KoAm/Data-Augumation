"""Feature corruption strategies used by VIME and comparison experiments."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np
from scipy.stats import norm, rankdata


class Corruptor(Protocol):
    def __call__(
        self, x: np.ndarray, mask: np.ndarray, rng: np.random.Generator
    ) -> np.ndarray: ...


@dataclass
class ColumnShuffleCorruptor:
    """VIME's empirical-marginal corruption: independently permute each column."""

    def __call__(
        self, x: np.ndarray, mask: np.ndarray, rng: np.random.Generator
    ) -> np.ndarray:
        x = np.asarray(x, dtype=np.float32)
        mask = np.asarray(mask, dtype=bool)
        if x.ndim != 2 or mask.shape != x.shape:
            raise ValueError("x and mask must be 2-D arrays with identical shapes")
        out = x.copy()
        for col in range(x.shape[1]):
            rows = np.flatnonzero(mask[:, col])
            if rows.size:
                out[rows, col] = x[rng.permutation(x.shape[0])[: rows.size], col]
        return out


class GaussianCopulaCorruptor:
    """Conditional Gaussian-copula sampler for continuous numeric features.

    Marginals are represented by empirical distributions and dependence by a
    regularized Gaussian copula. This implementation expects finite continuous
    columns; categorical columns should be handled by a mixed/discrete copula.
    """

    def __init__(self, shrinkage: float = 0.05, jitter: float = 1e-6):
        if not 0.0 <= shrinkage < 1.0:
            raise ValueError("shrinkage must be in [0, 1)")
        self.shrinkage = float(shrinkage)
        self.jitter = float(jitter)
        self._x: np.ndarray | None = None
        self._sorted: list[np.ndarray] | None = None
        self._corr: np.ndarray | None = None

    def fit(self, x: np.ndarray) -> "GaussianCopulaCorruptor":
        x = np.asarray(x, dtype=np.float64)
        if x.ndim != 2 or x.shape[0] < 2 or x.shape[1] < 1:
            raise ValueError("x must have at least 2 rows and 1 column")
        if not np.isfinite(x).all():
            raise ValueError("GaussianCopulaCorruptor requires finite values")
        self._x = x.copy()
        self._sorted = [np.sort(x[:, j]) for j in range(x.shape[1])]

        latent = np.empty_like(x)
        n = x.shape[0]
        for j in range(x.shape[1]):
            ranks = rankdata(x[:, j], method="average")
            u = np.clip((ranks - 0.5) / n, 1e-6, 1.0 - 1e-6)
            latent[:, j] = norm.ppf(u)
        p = x.shape[1]
        corr = np.eye(p, dtype=np.float64)
        for a in range(p):
            for b in range(a):
                sa, sb = latent[:, a].std(), latent[:, b].std()
                value = 0.0 if sa < 1e-12 or sb < 1e-12 else np.corrcoef(latent[:, a], latent[:, b])[0, 1]
                corr[a, b] = corr[b, a] = float(np.nan_to_num(value))
        corr = (1.0 - self.shrinkage) * corr + self.shrinkage * np.eye(p)
        eig_min = float(np.linalg.eigvalsh(corr).min())
        if eig_min < self.jitter:
            corr += (self.jitter - eig_min) * np.eye(p)
            scale = np.sqrt(np.diag(corr))
            corr = corr / np.outer(scale, scale)
        self._corr = corr
        return self

    def _to_latent(self, values: np.ndarray, col: int) -> np.ndarray:
        assert self._sorted is not None and self._x is not None
        sorted_x = self._sorted[col]
        left = np.searchsorted(sorted_x, values, side="left")
        right = np.searchsorted(sorted_x, values, side="right")
        u = np.clip((left + right) / (2.0 * len(sorted_x)), 1e-6, 1.0 - 1e-6)
        return norm.ppf(u)

    def _from_latent(self, values: np.ndarray, col: int) -> np.ndarray:
        assert self._sorted is not None
        u = np.clip(norm.cdf(values), 0.0, 1.0)
        return np.quantile(self._sorted[col], u, method="linear")

    def sample_conditional(
        self, x: np.ndarray, mask: np.ndarray, rng: np.random.Generator
    ) -> np.ndarray:
        if self._corr is None or self._x is None:
            raise RuntimeError("Call fit() before sampling")
        x = np.asarray(x, dtype=np.float64)
        mask = np.asarray(mask, dtype=bool)
        if x.ndim != 2 or x.shape != mask.shape or x.shape[1] != self._corr.shape[0]:
            raise ValueError("x/mask shape must match the fitted feature dimension")
        if not np.isfinite(x).all():
            raise ValueError("x must contain only finite values")

        out = x.copy()
        p = x.shape[1]
        for i in range(x.shape[0]):
            missing = np.flatnonzero(mask[i])
            observed = np.flatnonzero(~mask[i])
            if missing.size == 0:
                continue
            if observed.size == 0:
                conditional_mean = np.zeros(missing.size)
                conditional_cov = self._corr[np.ix_(missing, missing)]
            else:
                z_obs = np.array([self._to_latent(x[i, j], j) for j in observed])
                r_oo = self._corr[np.ix_(observed, observed)]
                r_mo = self._corr[np.ix_(missing, observed)]
                r_om = self._corr[np.ix_(observed, missing)]
                r_mm = self._corr[np.ix_(missing, missing)]
                solved_z = np.linalg.solve(r_oo + self.jitter * np.eye(observed.size), z_obs)
                solved_cross = np.linalg.solve(r_oo + self.jitter * np.eye(observed.size), r_om)
                conditional_mean = r_mo @ solved_z
                conditional_cov = r_mm - r_mo @ solved_cross
            conditional_cov = (conditional_cov + conditional_cov.T) / 2
            conditional_cov += self.jitter * np.eye(missing.size)
            # Explicit Cholesky sampling avoids NumPy's default SVD-based
            # multivariate_normal path, which is costly for wide tables.
            try:
                chol = np.linalg.cholesky(conditional_cov)
            except np.linalg.LinAlgError:
                chol = np.linalg.cholesky(
                    conditional_cov + max(self.jitter, 1e-8) * np.eye(missing.size)
                )
            z_missing = conditional_mean + chol @ rng.standard_normal(missing.size)
            for j, z in zip(missing, np.atleast_1d(z_missing)):
                out[i, j] = self._from_latent(np.asarray(z), int(j)).item()
        return out.astype(np.float32)

    def __call__(
        self, x: np.ndarray, mask: np.ndarray, rng: np.random.Generator
    ) -> np.ndarray:
        return self.sample_conditional(x, mask, rng)
