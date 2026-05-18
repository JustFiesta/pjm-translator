from __future__ import annotations

import numpy as np

from src.data.protocol import DatasetSource


def build_feature_matrix(source: DatasetSource) -> tuple[np.ndarray, np.ndarray]:
    """Consume a DatasetSource and return feature matrix and label array.

    Iterates all samples from ``source`` exactly once and stacks them into
    contiguous arrays ready for scikit-learn.

    Args:
        source: Any object satisfying the ``DatasetSource`` protocol.

    Returns:
        A tuple ``(X, y)`` where:
            - ``X``: float32 array of shape ``(n_samples, 234)``
            - ``y``: string array of shape ``(n_samples,)`` with sign labels

    Raises:
        ValueError: If ``source`` yields no samples.
    """
    vectors: list[np.ndarray] = []
    labels: list[str] = []

    for feature_vector, label in source.iter_samples():
        vectors.append(feature_vector)
        labels.append(label)

    if not vectors:
        raise ValueError("DatasetSource yielded no samples.")

    X = np.stack(vectors, axis=0)
    y = np.array(labels)
    return X, y
