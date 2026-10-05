"""PyTorch reimplementation of VIME's self- and semi-supervised pipeline."""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
from torch.utils.data import DataLoader, TensorDataset

from .corruption import ColumnShuffleCorruptor, Corruptor


@dataclass
class VIMEConfig:
    corruption_probability: float = 0.3
    reconstruction_weight: float = 2.0
    n_augmented_views: int = 3
    consistency_weight: float = 1.0
    self_epochs: int = 10
    semi_iterations: int = 1000
    batch_size: int = 128
    predictor_hidden_dim: int = 100
    encoder_hidden_dim: int | None = None
    encoder_depth: int = 1
    encoder_dropout: float = 0.0
    learning_rate: float = 1e-3
    patience: int = 100
    validation_fraction: float = 0.1
    device: str | None = None
    seed: int = 0


class VIMEPretextModel(nn.Module):
    """Shared encoder with mask-estimation and feature-reconstruction heads."""

    def __init__(
        self,
        input_dim: int,
        hidden_dim: int | None = None,
        depth: int = 1,
        dropout: float = 0.0,
    ):
        super().__init__()
        if depth < 1:
            raise ValueError("encoder_depth must be at least 1")
        hidden_dim = input_dim if hidden_dim is None else hidden_dim
        layers: list[nn.Module] = []
        in_dim = input_dim
        for layer_idx in range(depth):
            layers.append(nn.Linear(in_dim, hidden_dim))
            if layer_idx < depth - 1:
                layers.append(nn.ReLU())
                if dropout:
                    layers.append(nn.Dropout(dropout))
            elif depth == 1:
                # The official VIME encoder is a single Dense(dim, relu) layer.
                layers.append(nn.ReLU())
            in_dim = hidden_dim
        self.encoder = nn.Sequential(*layers)
        self.mask_estimator = nn.Linear(hidden_dim, input_dim)
        self.feature_estimator = nn.Linear(hidden_dim, input_dim)

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        z = self.encoder(x)
        return self.mask_estimator(z), torch.sigmoid(self.feature_estimator(z))


class VIMEPredictor(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int, n_classes: int):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, n_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.layers(x)


def _as_2d_float(x: np.ndarray, name: str) -> np.ndarray:
    x = np.asarray(x, dtype=np.float32)
    if x.ndim != 2 or not np.isfinite(x).all():
        raise ValueError(f"{name} must be a finite 2-D numeric array")
    return x


class VIMEClassifier:
    """VIME with injectable corruption, preserving the original training stages.

    Inputs should be scaled to [0, 1], matching the official MNIST pipeline and
    its sigmoid reconstruction head. For categorical data, encode categories
    before fitting and use a compatible reconstruction objective if necessary.
    """

    def __init__(self, config: VIMEConfig | None = None, corruptor: Corruptor | None = None):
        self.config = config or VIMEConfig()
        self.corruptor = corruptor or ColumnShuffleCorruptor()
        self.device = torch.device(self.config.device or ("mps" if torch.backends.mps.is_available() else "cpu"))
        self.rng = np.random.default_rng(self.config.seed)
        self.pretext: VIMEPretextModel | None = None
        self.predictor: VIMEPredictor | None = None
        self.classes_: np.ndarray | None = None
        self.history_: dict[str, list[float]] = {"self_loss": [], "train_loss": [], "val_loss": []}

    def _corrupt(self, x: np.ndarray, mask: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        corrupted = np.asarray(self.corruptor(x, mask, self.rng), dtype=np.float32)
        if corrupted.shape != x.shape or not np.isfinite(corrupted).all():
            raise ValueError("corruptor must return a finite array with the same shape as x")
        actual_mask = (x != corrupted).astype(np.float32)
        return actual_mask, corrupted

    def pretrain(self, x_unlabeled: np.ndarray) -> "VIMEClassifier":
        x = _as_2d_float(x_unlabeled, "x_unlabeled")
        torch.manual_seed(self.config.seed)
        fit_corruptor = getattr(self.corruptor, "fit", None)
        if callable(fit_corruptor):
            fit_corruptor(x)
        self.pretext = VIMEPretextModel(
            x.shape[1],
            hidden_dim=self.config.encoder_hidden_dim,
            depth=self.config.encoder_depth,
            dropout=self.config.encoder_dropout,
        ).to(self.device)

        # The official VIME code constructs one corrupted pretext dataset before fit().
        requested_mask = self.rng.binomial(1, self.config.corruption_probability, x.shape).astype(bool)
        mask, x_tilde = self._corrupt(x, requested_mask)
        dataset = TensorDataset(
            torch.from_numpy(x_tilde), torch.from_numpy(mask), torch.from_numpy(x)
        )
        loader = DataLoader(
            dataset,
            batch_size=self.config.batch_size,
            shuffle=True,
            generator=torch.Generator().manual_seed(self.config.seed),
        )
        optimizer = torch.optim.RMSprop(self.pretext.parameters())
        for _ in range(self.config.self_epochs):
            self.pretext.train()
            epoch_losses = []
            for xb, mb, target in loader:
                xb, mb, target = xb.to(self.device), mb.to(self.device), target.to(self.device)
                mask_logits, reconstructed = self.pretext(xb)
                loss = F.binary_cross_entropy_with_logits(mask_logits, mb)
                loss = loss + self.config.reconstruction_weight * F.mse_loss(reconstructed, target)
                optimizer.zero_grad(set_to_none=True)
                loss.backward()
                optimizer.step()
                epoch_losses.append(float(loss.detach().cpu()))
            self.history_["self_loss"].append(float(np.mean(epoch_losses)))
        return self

    def fit(
        self,
        x_labeled: np.ndarray,
        y_labeled: np.ndarray,
        x_unlabeled: np.ndarray,
        x_validation: np.ndarray | None = None,
        y_validation: np.ndarray | None = None,
    ) -> "VIMEClassifier":
        x_l = _as_2d_float(x_labeled, "x_labeled")
        x_u = _as_2d_float(x_unlabeled, "x_unlabeled")
        y = np.asarray(y_labeled).reshape(-1)
        if x_l.shape[0] != y.shape[0] or x_l.shape[1] != x_u.shape[1]:
            raise ValueError("labeled/unlabeled features and labels have incompatible shapes")
        if self.pretext is None:
            self.pretrain(x_u)
        assert self.pretext is not None

        classes, y_idx = np.unique(y, return_inverse=True)
        self.classes_ = classes
        x_val = None if x_validation is None else _as_2d_float(x_validation, "x_validation")
        y_val = None if y_validation is None else np.asarray(y_validation).reshape(-1)
        if (x_val is None) != (y_val is None):
            raise ValueError("provide both x_validation and y_validation, or neither")
        if x_val is None:
            order = self.rng.permutation(len(x_l))
            n_val = (
                max(1, int(round(len(order) * self.config.validation_fraction)))
                if len(order) > 3 and self.config.validation_fraction > 0
                else 0
            )
            if n_val:
                val_idx, train_idx = order[:n_val], order[n_val:]
                x_val, y_val = x_l[val_idx], y[ val_idx]
                x_l, y_idx = x_l[train_idx], y_idx[train_idx]
        y_val_idx = None
        if y_val is not None:
            mapping = {label: i for i, label in enumerate(classes)}
            try:
                y_val_idx = np.asarray([mapping[label] for label in y_val], dtype=np.int64)
            except KeyError as exc:
                raise ValueError("validation labels must occur in the labeled training data") from exc

        self.pretext.eval()
        for parameter in self.pretext.parameters():
            parameter.requires_grad_(False)
        with torch.no_grad():
            z_l = self.pretext.encoder(torch.from_numpy(x_l).to(self.device))
            z_u = self.pretext.encoder(torch.from_numpy(x_u).to(self.device))
            z_val = None if x_val is None else self.pretext.encoder(torch.from_numpy(x_val).to(self.device))

        self.predictor = VIMEPredictor(
            z_l.shape[1], self.config.predictor_hidden_dim, len(classes)
        ).to(self.device)
        optimizer = torch.optim.Adam(self.predictor.parameters(), lr=self.config.learning_rate)
        y_tensor = torch.as_tensor(y_idx, dtype=torch.long, device=self.device)
        best_loss, best_state, best_step = float("inf"), None, -1

        for step in range(self.config.semi_iterations):
            self.predictor.train()
            batch_idx = self.rng.integers(0, len(z_l), size=min(self.config.batch_size, len(z_l)))
            u_idx = self.rng.integers(0, len(z_u), size=min(self.config.batch_size, len(z_u)))
            logits_l = self.predictor(z_l[batch_idx])
            supervised = F.cross_entropy(logits_l, y_tensor[batch_idx])

            xu = x_u[u_idx]
            views = []
            for _ in range(self.config.n_augmented_views):
                mask = self.rng.binomial(
                    1, self.config.corruption_probability, xu.shape
                ).astype(bool)
                _, corrupted = self._corrupt(xu, mask)
                with torch.no_grad():
                    views.append(self.pretext.encoder(torch.from_numpy(corrupted).to(self.device)))
            z_views = torch.stack(views, dim=0)
            unlabeled_logits = self.predictor(z_views.reshape(-1, z_views.shape[-1])).reshape(
                self.config.n_augmented_views, -1, len(classes)
            )
            consistency = unlabeled_logits.var(dim=0, unbiased=False).mean()
            loss = supervised + self.config.consistency_weight * consistency
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            optimizer.step()
            self.history_["train_loss"].append(float(loss.detach().cpu()))

            if z_val is not None and y_val_idx is not None:
                self.predictor.eval()
                with torch.no_grad():
                    val_loss = float(
                        F.cross_entropy(
                            self.predictor(z_val),
                            torch.as_tensor(y_val_idx, dtype=torch.long, device=self.device),
                        ).cpu()
                    )
                self.history_["val_loss"].append(val_loss)
                if val_loss < best_loss:
                    best_loss = val_loss
                    best_state = {k: v.detach().cpu().clone() for k, v in self.predictor.state_dict().items()}
                    best_step = step
                elif self.config.patience and step - best_step >= self.config.patience:
                    break

        if best_state is not None:
            self.predictor.load_state_dict(best_state)
        return self

    def predict_proba(self, x: np.ndarray) -> np.ndarray:
        if self.pretext is None or self.predictor is None or self.classes_ is None:
            raise RuntimeError("Call fit() before predict_proba()")
        x = _as_2d_float(x, "x")
        self.pretext.eval()
        self.predictor.eval()
        with torch.no_grad():
            z = self.pretext.encoder(torch.from_numpy(x).to(self.device))
            probs = self.predictor(z).softmax(dim=-1)
        return probs.cpu().numpy()

    def predict(self, x: np.ndarray) -> np.ndarray:
        assert self.classes_ is not None
        return self.classes_[self.predict_proba(x).argmax(axis=1)]
