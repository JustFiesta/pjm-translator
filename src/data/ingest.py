from __future__ import annotations

from pathlib import Path
from typing import Iterator

import numpy as np
import pandas as pd

LABEL_COL = "label"
EXPECTED_FEATURE_DIM = 784   # 28 × 28 grayscale pixels


def _label_to_letter(raw_label: int) -> str:
    """Convert a Sign Language MNIST integer label to an ASL letter string.

    The dataset encodes letters as integers 0–24, skipping 9 (J) and 25 (Z)
    because both require motion.  ``chr(ord('A') + raw_label)`` maps cleanly:
    0→'A', 1→'B', …, 8→'I', 10→'K', …, 24→'Y'.

    Args:
        raw_label: Integer class label from the CSV.

    Returns:
        Single uppercase ASCII letter string.
    """
    return chr(ord("A") + int(raw_label))


class CsvDataset:
    """Sign Language MNIST CSV dataset implementing the DatasetSource protocol.

    Loads a raw CSV file (``sign_mnist_train.csv`` or ``sign_mnist_test.csv``),
    normalises pixel values to ``[0, 1]``, and exposes labelled feature vectors.

    Args:
        csv_path: Path to the CSV file (e.g. ``data/sign_mnist_train.csv``).

    Raises:
        FileNotFoundError: If ``csv_path`` does not exist.
        ValueError: If the ``label`` column is missing or feature count is wrong.
    """

    def __init__(self, csv_path: Path) -> None:
        if not csv_path.exists():
            raise FileNotFoundError(f"Dataset CSV not found: {csv_path}")

        df = pd.read_csv(csv_path)

        if LABEL_COL not in df.columns:
            raise ValueError(
                f"Required column '{LABEL_COL}' not found in {csv_path}. "
                f"Available columns: {list(df.columns)}"
            )

        feature_cols = [c for c in df.columns if c != LABEL_COL]
        if len(feature_cols) != EXPECTED_FEATURE_DIM:
            raise ValueError(
                f"Expected {EXPECTED_FEATURE_DIM} feature columns, "
                f"got {len(feature_cols)} in {csv_path}."
            )

        # Normalise pixel values from [0, 255] to [0.0, 1.0].
        self._features: np.ndarray = (
            df[feature_cols].to_numpy(dtype=np.float32) / 255.0
        )
        self._labels: np.ndarray = np.array(
            [_label_to_letter(v) for v in df[LABEL_COL]]
        )

    def __len__(self) -> int:
        """Return the number of samples in the dataset."""
        return len(self._labels)

    def iter_samples(self) -> Iterator[tuple[np.ndarray, str]]:
        """Yield one (feature_vector, label) pair per sample.

        Yields:
            A tuple of:
                - feature_vector: float32 array of shape ``(784,)``, values in ``[0, 1]``
                - label: single uppercase letter string (e.g. ``"A"``)
        """
        for features, label in zip(self._features, self._labels):
            yield features, str(label)
