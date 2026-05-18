from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import numpy as np
from sklearn.svm import SVC

DEFAULT_ARTIFACT = Path("artifacts/model.pkl")


def train_and_save(
    X_train: np.ndarray,
    y_train: np.ndarray,
    output_path: Path = DEFAULT_ARTIFACT,
) -> None:
    """Train an SVC classifier and persist it to disk.

    Args:
        X_train: Feature matrix of shape ``(n_samples, 234)``.
        y_train: Label array of shape ``(n_samples,)``.
        output_path: Destination ``.pkl`` path for the serialised model.

    Raises:
        ValueError: If ``X_train`` and ``y_train`` have different lengths.
    """
    if len(X_train) != len(y_train):
        raise ValueError(
            f"X_train and y_train must have the same length, "
            f"got {len(X_train)} and {len(y_train)}."
        )

    clf = SVC(kernel="rbf", C=10.0, gamma="scale", probability=False)
    clf.fit(X_train, y_train)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(clf, output_path)
    print(f"Model saved to {output_path}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train PJM sign classifier.")
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("data/raw/550-points.csv"),
        help="Path to the raw CSV file.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_ARTIFACT,
        help="Destination path for the saved model.",
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
    train_and_save(X_train, y_train, args.output)
