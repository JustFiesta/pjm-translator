from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC

DEFAULT_ARTIFACT = Path("artifacts/model.pkl")

CLASSIFIERS = {
    "svc": lambda: SVC(kernel="rbf", C=10.0, gamma="scale", probability=False),
    "rf": lambda: RandomForestClassifier(n_estimators=200, n_jobs=-1, random_state=42),
}


def build_classifier(name: str) -> object:
    """Instantiate a classifier by name.

    Args:
        name: One of ``"svc"`` or ``"rf"``.

    Returns:
        Unfitted sklearn estimator.

    Raises:
        ValueError: If ``name`` is not a recognised classifier key.
    """
    if name not in CLASSIFIERS:
        raise ValueError(
            f"Unknown classifier '{name}'. Choose from: {list(CLASSIFIERS)}"
        )
    return CLASSIFIERS[name]()


def train_and_save(
    X_train: np.ndarray,
    y_train: np.ndarray,
    output_path: Path = DEFAULT_ARTIFACT,
    classifier: str = "svc",
) -> None:
    """Train a classifier and persist it to disk.

    Args:
        X_train: Feature matrix of shape ``(n_samples, 784)``.
        y_train: Label array of shape ``(n_samples,)``.
        output_path: Destination ``.pkl`` path for the serialised model.
        classifier: Classifier name — ``"svc"`` (default) or ``"rf"``.

    Raises:
        ValueError: If ``X_train`` and ``y_train`` have different lengths,
            or ``classifier`` is not recognised.
    """
    if len(X_train) != len(y_train):
        raise ValueError(
            f"X_train and y_train must have the same length, "
            f"got {len(X_train)} and {len(y_train)}."
        )

    clf = build_classifier(classifier)
    print(f"Classifier: {clf.__class__.__name__}")
    clf.fit(X_train, y_train)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(clf, output_path)
    print(f"Model saved to {output_path}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train sign-language classifier.")
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("data/raw/sign_mnist_train.csv"),
        help="Path to the raw CSV file.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_ARTIFACT,
        help="Destination path for the saved model.",
    )
    parser.add_argument(
        "--classifier",
        choices=list(CLASSIFIERS),
        default="svc",
        help="Classifier to train (default: svc).",
    )
    return parser.parse_args()


if __name__ == "__main__":
    from src.data.extract import build_feature_matrix
    from src.data.ingest import CsvDataset
    from src.data.split import stratified_split

    args = _parse_args()
    print(f"Loading dataset: {args.dataset}")
    X, y = build_feature_matrix(CsvDataset(args.dataset))
    X_train, _, _, y_train, _, _ = stratified_split(X, y)
    print(f"Training on {len(X_train)} samples …")
    train_and_save(X_train, y_train, args.output, args.classifier)
