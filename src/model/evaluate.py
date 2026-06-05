from __future__ import annotations

from typing import Protocol

import numpy as np
from sklearn.metrics import accuracy_score, classification_report


class Predictor(Protocol):
    """Minimal prediction interface required by ``evaluate``."""

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Return predicted labels for an input feature matrix."""


def evaluate(
    clf: Predictor,
    X_test: np.ndarray,
    y_test: np.ndarray,
) -> dict[str, object]:
    """Evaluate a trained classifier on the test set and print a report.

    Args:
        clf: A fitted predictor object with a ``predict`` method.
        X_test: Feature matrix of shape ``(n_samples, 784)``.
        y_test: True label array of shape ``(n_samples,)``.

    Returns:
        A dict with keys:
            - ``"accuracy"``: overall accuracy as a float
            - ``"report"``: full per-class classification report as a string

    Raises:
        ValueError: If ``X_test`` and ``y_test`` have different lengths.
    """
    if len(X_test) != len(y_test):
        raise ValueError(
            f"X_test and y_test must have the same length, "
            f"got {len(X_test)} and {len(y_test)}."
        )

    y_pred = clf.predict(X_test)
    accuracy = float(accuracy_score(y_test, y_pred))
    report = classification_report(y_test, y_pred, zero_division=0)

    print(f"Accuracy: {accuracy:.4f}")
    print(report)

    return {"accuracy": accuracy, "report": report}
