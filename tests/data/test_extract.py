from __future__ import annotations

import numpy as np
import pytest

from src.data.extract import build_feature_matrix
from src.data.ingest import EXPECTED_FEATURE_DIM


def test_build_feature_matrix_returns_correct_shapes(synthetic_dataset) -> None:
    # Arrange — synthetic_dataset has 30 samples, 234 features (from conftest)

    # Act
    X, y = build_feature_matrix(synthetic_dataset)

    # Assert
    assert X.shape == (30, EXPECTED_FEATURE_DIM)
    assert y.shape == (30,)


def test_build_feature_matrix_x_dtype_is_float32(synthetic_dataset) -> None:
    # Arrange + Act
    X, _ = build_feature_matrix(synthetic_dataset)

    # Assert
    assert X.dtype == np.float32


def test_build_feature_matrix_y_contains_strings(synthetic_dataset) -> None:
    # Arrange + Act
    _, y = build_feature_matrix(synthetic_dataset)

    # Assert
    assert all(isinstance(label, str) for label in y)


def test_build_feature_matrix_raises_on_empty_source() -> None:
    # Arrange — source that yields nothing
    class _EmptySource:
        def iter_samples(self):
            return iter([])

    # Act + Assert
    with pytest.raises(ValueError, match="no samples"):
        build_feature_matrix(_EmptySource())


def test_build_feature_matrix_single_sample() -> None:
    # Arrange
    vector = np.ones(EXPECTED_FEATURE_DIM, dtype=np.float32)

    class _SingleSource:
        def iter_samples(self):
            yield vector, "A"

    # Act
    X, y = build_feature_matrix(_SingleSource())

    # Assert
    assert X.shape == (1, EXPECTED_FEATURE_DIM)
    assert y[0] == "A"
