#!/usr/bin/env python3
"""Repeated, paired comparison of tabular semi-supervised methods."""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from scipy.stats import bootstrap
from sklearn.compose import ColumnTransformer
from sklearn.datasets import load_breast_cancer, load_digits, load_wine
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM_CC = ROOT / "upstream" / "Tabular-Class-Conditioned-SSL"
sys.path.insert(0, str(UPSTREAM_CC))

# Keep the pinned upstream checkout pristine despite its import-time directory creation.
_original_makedirs = os.makedirs


def _redirect_experiments(path, *args, **kwargs):
    if Path(path).resolve() == (UPSTREAM_CC / "experiments").resolve():
        path = ROOT / "results" / "official_cc_experiments"
    return _original_makedirs(path, *args, **kwargs)


os.makedirs = _redirect_experiments
import utils as cc_utils  # noqa: E402
import training as cc_training  # noqa: E402
from corruption_mask_generators import RandomMaskGenerator  # noqa: E402
from dataset_samplers import ClassCorruptSampler, SupervisedSampler  # noqa: E402
from model import Neural_Net  # noqa: E402
os.makedirs = _original_makedirs

from tabular_research.corruption import GaussianCopulaCorruptor  # noqa: E402
from tabular_research.vime_torch import VIMEClassifier, VIMEConfig  # noqa: E402

METHODS = (
    "vime_column_shuffle",
    "vime_gaussian_copula",
    "class_conditioned_contrastive_official",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", type=int, nargs="+", default=[11, 23, 37, 51, 67])
    parser.add_argument("--datasets", nargs="+", choices=("breast_cancer", "wine", "digits"),
                        default=["breast_cancer", "wine"])
    parser.add_argument("--labeled-fraction", type=float, default=0.3)
    parser.add_argument("--epochs", type=int, default=15)
    parser.add_argument("--vime-iterations", type=int, default=300)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--output", type=Path, default=ROOT / "results" / "repeated_compare.json")
    return parser.parse_args()


def load_dataset(name: str) -> tuple[np.ndarray, np.ndarray]:
    loaders = {
        "breast_cancer": load_breast_cancer,
        "wine": load_wine,
        "digits": load_digits,
    }
    dataset = loaders[name]()
    return np.asarray(dataset.data, dtype=np.float32), np.asarray(dataset.target, dtype=int)


def score(y_true: np.ndarray, probabilities: np.ndarray) -> dict[str, float]:
    pred = probabilities.argmax(axis=1)
    n_classes = probabilities.shape[1]
    auc = (
        roc_auc_score(y_true, probabilities[:, 1])
        if n_classes == 2
        else roc_auc_score(y_true, probabilities, multi_class="ovr", average="macro")
    )
    return {
        "accuracy": float(accuracy_score(y_true, pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, pred)),
        "macro_f1": float(f1_score(y_true, pred, average="macro")),
        "macro_roc_auc_ovr": float(auc),
    }


def reset_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def run_one(dataset_name: str, seed: int, args: argparse.Namespace) -> dict:
    reset_seed(seed)
    x, y = load_dataset(dataset_name)
    indices = np.arange(len(y))
    train_idx, test_idx = train_test_split(
        indices, test_size=0.2, stratify=y, random_state=seed
    )
    train_l_idx, train_u_idx = train_test_split(
        train_idx,
        train_size=args.labeled_fraction,
        stratify=y[train_idx],
        random_state=seed + 100_003,
    )
    scaler = MinMaxScaler()
    x_train = scaler.fit_transform(x[train_idx]).astype(np.float32)
    x_test = scaler.transform(x[test_idx]).astype(np.float32)
    train_positions = {index: position for position, index in enumerate(train_idx)}
    labeled_pos = np.array([train_positions[i] for i in train_l_idx])
    unlabeled_pos = np.array([train_positions[i] for i in train_u_idx])
    x_l, y_l = x_train[labeled_pos], y[train_l_idx]
    x_u = x_train[unlabeled_pos]
    n_classes = int(np.unique(y).size)

    config = VIMEConfig(
        corruption_probability=0.4,
        reconstruction_weight=2.0,
        n_augmented_views=3,
        consistency_weight=1.0,
        self_epochs=args.epochs,
        semi_iterations=args.vime_iterations,
        batch_size=args.batch_size,
        predictor_hidden_dim=32,
        encoder_hidden_dim=32,
        encoder_depth=4,
        encoder_dropout=0.0,
        validation_fraction=0.0,
        device="cpu",
        seed=seed,
    )
    metric_results: dict[str, dict[str, float]] = {}
    for method_name, corruptor in (
        ("vime_column_shuffle", None),
        ("vime_gaussian_copula", GaussianCopulaCorruptor()),
    ):
        reset_seed(seed)
        estimator = VIMEClassifier(config=config, corruptor=corruptor)
        estimator.fit(x_l, y_l, x_u)
        metric_results[method_name] = score(y[test_idx], estimator.predict_proba(x_test))

    # Use the authors' class-conditioned contrastive implementation unchanged.
    reset_seed(seed)
    cc_utils.DEVICE = torch.device("cpu")
    cc_utils.BATCH_SIZE = args.batch_size
    cc_utils.CORRUPTION_RATE = 0.4
    cc_utils.CONTRASTIVE_LEARNING_MAX_EPOCHS = args.epochs
    cc_utils.SUPERVISED_LEARNING_MAX_EPOCHS = args.epochs
    cc_utils.CLS_CORR_REFRESH_SAMPLER_PERIOD = 10
    cc_training.BATCH_SIZE = args.batch_size
    cc_training.CONTRASTIVE_LEARNING_MAX_EPOCHS = args.epochs
    cc_training.SUPERVISED_LEARNING_MAX_EPOCHS = args.epochs
    cc_training.CLS_CORR_REFRESH_SAMPLER_PERIOD = 10

    columns = [f"feature_{i}" for i in range(x_train.shape[1])]
    train_frame = pd.DataFrame(x_train, columns=columns)
    labeled_frame = train_frame.iloc[labeled_pos].reset_index(drop=True)
    identity_transform = ColumnTransformer(
        [("numeric", "passthrough", columns)], remainder="drop"
    ).fit(train_frame)
    supervised_sampler = SupervisedSampler(labeled_frame, y_l.astype(int))
    bootstrap_model = nn.DataParallel(
        Neural_Net(input_dim=x_train.shape[1], emb_dim=32, output_dim=n_classes)
    )
    bootstrap_model.module.freeze_encoder()
    cc_training.train_classification(bootstrap_model, supervised_sampler, identity_transform)
    bootstrap_targets = cc_utils.get_bootstrapped_targets(
        train_frame, y[train_idx].astype(int), bootstrap_model,
        np.isin(train_idx, train_l_idx), identity_transform,
    )
    class_sampler = ClassCorruptSampler(train_frame, bootstrap_targets.astype(int))
    cc_model = nn.DataParallel(
        Neural_Net(input_dim=x_train.shape[1], emb_dim=32, output_dim=n_classes)
    )
    cc_training.train_contrastive_loss(
        cc_model,
        "cls_corr-rand_feats",
        class_sampler,
        supervised_sampler,
        RandomMaskGenerator(x_train.shape[1]),
        np.isin(train_idx, train_l_idx),
        identity_transform,
    )
    cc_model.module.freeze_encoder()
    cc_training.train_classification(cc_model, supervised_sampler, identity_transform)
    cc_model.module.eval()
    with torch.no_grad():
        logits = cc_model.module.get_classification_prediction_logits(torch.from_numpy(x_test))
        cc_probs = logits.softmax(dim=1).cpu().numpy()
    metric_results["class_conditioned_contrastive_official"] = score(y[test_idx], cc_probs)

    return {
        "dataset": dataset_name,
        "seed": seed,
        "n_total": int(len(y)),
        "n_train": int(len(train_idx)),
        "n_labeled": int(len(train_l_idx)),
        "n_unlabeled": int(len(train_u_idx)),
        "n_test": int(len(test_idx)),
        "n_features": int(x.shape[1]),
        "n_classes": n_classes,
        "metrics": metric_results,
    }


def summarize(runs: list[dict]) -> dict:
    metrics = ("accuracy", "balanced_accuracy", "macro_f1", "macro_roc_auc_ovr")
    summary = {}
    for dataset_name in sorted({run["dataset"] for run in runs}):
        dataset_runs = [run for run in runs if run["dataset"] == dataset_name]
        summary[dataset_name] = {}
        for method in METHODS:
            summary[dataset_name][method] = {}
            for metric in metrics:
                values = np.array([r["metrics"][method][metric] for r in dataset_runs])
                summary[dataset_name][method][metric] = {
                    "mean": float(values.mean()),
                    "std": float(values.std(ddof=1)) if len(values) > 1 else 0.0,
                    "median": float(np.median(values)),
                }
        # Paired differences preserve each seed's shared split and labeled subset.
        summary[dataset_name]["paired_vs_vime_column_shuffle"] = {}
        baseline = "vime_column_shuffle"
        for method in METHODS[1:]:
            summary[dataset_name]["paired_vs_vime_column_shuffle"][method] = {}
            for metric in metrics:
                differences = np.array([
                    r["metrics"][method][metric] - r["metrics"][baseline][metric]
                    for r in dataset_runs
                ])
                if len(differences) > 1:
                    ci = bootstrap(
                        (differences,), np.mean, confidence_level=0.95,
                        n_resamples=10_000, method="percentile", random_state=2026,
                    ).confidence_interval
                    low, high = float(ci.low), float(ci.high)
                else:
                    low = high = None
                summary[dataset_name]["paired_vs_vime_column_shuffle"][method][metric] = {
                    "mean_difference": float(differences.mean()),
                    "bootstrap_95pct_ci": [low, high],
                    "seed_differences": differences.tolist(),
                }
    return summary


def main() -> None:
    args = parse_args()
    if not 0 < args.labeled_fraction < 1:
        raise ValueError("labeled-fraction must be between zero and one")
    runs = []
    for dataset_name in args.datasets:
        for seed in args.seeds:
            print(f"Running {dataset_name}, seed={seed}", flush=True)
            runs.append(run_one(dataset_name, seed, args))
    result = {
        "protocol": {
            "datasets": args.datasets,
            "seeds": args.seeds,
            "repeated_stratified_holdout": "80/20 test split; within each training split, stratified labeled subset",
            "labeled_fraction": args.labeled_fraction,
            "epochs": args.epochs,
            "vime_self_epochs": args.epochs,
            "vime_iterations": args.vime_iterations,
            "batch_size": args.batch_size,
            "encoder": "same 4-layer, 32-wide MLP for all methods",
            "preprocessing": "MinMaxScaler fit separately on each training split; shared split/subset among methods",
            "primary_metric": "macro_roc_auc_ovr",
            "metrics": ["macro_roc_auc_ovr", "balanced_accuracy", "macro_f1", "accuracy"],
            "class_conditioned_refresh_period": 10,
        },
        "runs": runs,
        "summary": summarize(runs),
        "interpretation_note": (
            "Exploratory comparison across two built-in numeric datasets and repeated holdouts. "
            "Bootstrap intervals summarize seed-to-seed paired differences, but overlapping holdouts "
            "are not independent; this is not a confirmatory significance test. Dataset-specific "
            "means and consistency across datasets matter more than pooled ranking."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False), encoding="utf-8")
    print(json.dumps(result["summary"], indent=2))
    print(f"Saved {args.output}")


if __name__ == "__main__":
    main()
