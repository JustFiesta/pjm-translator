from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from src.data.ingest import EXPECTED_FEATURE_DIM, CsvDataset


def test_csv_dataset_loads_file(tmp_path: Path) -> None:
    csv_file = tmp_path / "test.csv"
    csv_file.write_text(_make_csv(n_rows=5))

    ds = CsvDataset(csv_file)

    assert len(ds) == 5


def test_csv_dataset_iter_samples_yields_correct_shape(tmp_path: Path) -> None:
    csv_file = tmp_path / "test.csv"
    csv_file.write_text(_make_csv(n_rows=3))
    ds = CsvDataset(csv_file)

    samples = list(ds.iter_samples())

    assert len(samples) == 3
    for vector, label in samples:
        assert vector.shape == (EXPECTED_FEATURE_DIM,)
        assert vector.dtype == np.float32
        assert isinstance(label, str)
        assert len(label) == 1


def test_csv_dataset_normalises_pixels(tmp_path: Path) -> None:
    csv_file = tmp_path / "test.csv"
    csv_file.write_text(_make_csv(n_rows=2))
    ds = CsvDataset(csv_file)

    vectors = [v for v, _ in ds.iter_samples()]

    # Pixel values must be in [0, 1] after normalisation.
    for v in vectors:
        assert v.min() >= 0.0
        assert v.max() <= 1.0


def test_csv_dataset_converts_label_to_letter(tmp_path: Path) -> None:
    csv_file = tmp_path / "test.csv"
    # Label 0 → 'A', label 1 → 'B'
    csv_file.write_text(_make_csv(n_rows=2, labels=[0, 1]))
    ds = CsvDataset(csv_file)

    labels = [lbl for _, lbl in ds.iter_samples()]

    assert labels == ["A", "B"]


def test_csv_dataset_raises_on_missing_file() -> None:
    missing = Path("data/raw/does_not_exist.csv")

    with pytest.raises(FileNotFoundError, match="does_not_exist"):
        CsvDataset(missing)


def test_csv_dataset_raises_on_missing_label_column(tmp_path: Path) -> None:
    header = ",".join(f"pixel{i}" for i in range(1, EXPECTED_FEATURE_DIM + 1))
    row = ",".join("128" for _ in range(EXPECTED_FEATURE_DIM))
    csv_file = tmp_path / "no_label.csv"
    csv_file.write_text(f"{header}\n{row}\n")

    with pytest.raises(ValueError, match="label"):
        CsvDataset(csv_file)


def test_csv_dataset_raises_on_wrong_feature_count(tmp_path: Path) -> None:
    header = "label," + ",".join(f"pixel{i}" for i in range(1, 11))
    row = "0," + ",".join("128" for _ in range(10))
    csv_file = tmp_path / "short.csv"
    csv_file.write_text(f"{header}\n{row}\n")

    with pytest.raises(ValueError, match="784"):
        CsvDataset(csv_file)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_csv(
    n_rows: int,
    labels: list[int] | None = None,
) -> str:
    """Build a minimal valid Sign Language MNIST CSV string."""
    pixel_cols = ",".join(f"pixel{i}" for i in range(1, EXPECTED_FEATURE_DIM + 1))
    header = f"label,{pixel_cols}"
    rows = []
    for i in range(n_rows):
        lbl = labels[i] if labels else 0
        pixels = ",".join("128" for _ in range(EXPECTED_FEATURE_DIM))
        rows.append(f"{lbl},{pixels}")
    return "\n".join([header] + rows) + "\n"
