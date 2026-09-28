# Tabular research benchmark

This directory preserves the two author repositories under `upstream/` at the
fixed revisions in [UPSTREAM_VERSIONS.md](UPSTREAM_VERSIONS.md). The source
checkouts are detached at those commits and are not edited by this work.

## PyTorch VIME

`src/tabular_research/vime_torch.py` ports the official VIME pipeline:

1. Self-supervised pretraining estimates the corruption mask and reconstructs
   the original features from corrupted unlabeled rows.
2. The encoder is frozen. A predictor learns from labeled rows while its logits
   are regularized to agree across multiple corruptions of each unlabeled row.

The default encoder and objectives follow the official code. `VIMEClassifier`
accepts an injected corruption strategy, so the replacement sampler can be
changed without rewriting the training loop. Inputs should be finite and scaled
to `[0, 1]`, as in the original MNIST example and its sigmoid reconstruction
head.

## Copula corruption

`src/tabular_research/corruption.py` includes:

- `ColumnShuffleCorruptor`, which independently samples each feature from its
  empirical marginal, matching VIME's corruption behavior.
- `GaussianCopulaCorruptor`, which estimates empirical marginal distributions
  and a regularized Gaussian copula, then samples masked continuous values
  conditional on observed values.

The Gaussian copula is the only copula family implemented and tested in the
current downstream comparison. It is a practical, relatively parsimonious
starting point, not a demonstrated universal optimum. See the detailed
[Japanese copula analysis and procedure](results/EXPERIMENT_DETAILED_JA.md).

The included copula currently supports continuous finite numeric features. It
does not model categorical features or guarantee that an augmented row keeps
its class label. Those need explicit handling and evaluation before research
claims are made.

## Environment and repeated comparison

From this directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-lock.txt
scripts/run_quick_compare.sh --epochs 15 --vime-iterations 300
```

The runner compares standard VIME corruption, copula VIME corruption, and the
authors' class-conditioned contrastive training code over five seeds on both
Breast Cancer Wisconsin and Wine. Each method uses the same stratified test
split and labeled subset per seed, the same four-layer, 32-wide encoder,
preprocessing, and training budget. It reports mean, standard deviation, and
paired seed-level differences for macro ROC-AUC, balanced accuracy, macro F1,
and accuracy.

Results are in the detailed [Japanese experiment report](results/REPORT_JA.md)
and the full [results JSON](results/repeated_compare.json).
The bootstrap intervals describe variation across five paired seeds; because
the repeated holdouts overlap, they are exploratory, not a confirmatory
significance test. On these settings, Gaussian-copula VIME is slightly ahead
of standard VIME on both datasets, but the paired intervals include zero. The
official class-conditioned contrastive method is much lower on Breast Cancer,
while it has the highest mean macro ROC-AUC on Wine; its Wine interval also
includes zero. The current evidence therefore does not establish a general
winner. Digits is available via `--datasets digits`, but omitted from this run
because conditional copula sampling is computationally expensive at 64
features.

These are fixed-budget comparisons, not independently hyperparameter-tuned
leaderboards. Stronger claims need more datasets, proper nested validation,
repeated cross-validation, and confirmatory statistical analysis.

The second repository is older research code without a dependency lockfile.
Compatibility with current package releases may require small environment
adjustments; the upstream source remains unchanged for traceability.
