from __future__ import annotations

from sklearn.svm import SVC


def build_svc_classifier() -> SVC:
    """Build the default SVC classifier for sign classification."""
    return SVC(kernel="rbf", C=10.0, gamma="scale", probability=False)
