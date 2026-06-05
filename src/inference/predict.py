from __future__ import annotations

from pathlib import Path
from typing import Protocol

import joblib
import numpy as np

from src.inference.protocol import FeatureSource
from src.model.classifiers.cnn import load_cnn_predictor


class Predictor(Protocol):
    """Minimal prediction interface used by inference and evaluation."""

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Return predicted labels for input features."""


def load_model(path: Path) -> Predictor:
    """Load a serialised classifier/predictor artifact from disk.

    Args:
        path: Path to a ``.pkl`` (sklearn) or ``.keras`` (CNN) artifact.

    Returns:
        Predictor object exposing ``predict``.

    Raises:
        FileNotFoundError: If ``path`` does not exist.
    """
    if path.suffix == ".keras":
        labels_path = path.with_suffix(".labels.json")
        return load_cnn_predictor(path, labels_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Model artifact not found: {path}. "
            "Run 'uv run python -m src.model.train' first."
        )
    return joblib.load(path)


def predict_sign(clf: Predictor, source: FeatureSource) -> str:
    """Classify one feature vector obtained from ``source``.

    Reads a single 784-dim vector from ``source``, passes it through the
    classifier, and returns the predicted sign label.  The caller is
    responsible for calling ``source.release()`` when done.

    Args:
        clf: A fitted predictor (loaded via ``load_model``).
        source: Any object satisfying the ``FeatureSource`` protocol.

    Returns:
        Predicted sign label as a Polish string (e.g. ``"A"``).
    """
    vector = source.read_features()
    return str(clf.predict(vector.reshape(1, -1))[0])
