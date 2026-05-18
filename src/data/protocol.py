from __future__ import annotations

from typing import TYPE_CHECKING, Iterator, Protocol

if TYPE_CHECKING:
    import numpy as np


class DatasetSource(Protocol):
    """Source of labelled training samples for the PJM classifier.

    Any object that implements ``iter_samples`` satisfies this protocol —
    no inheritance required.  Current implementation: ``CsvDataset``.
    """

    def iter_samples(self) -> Iterator[tuple[np.ndarray, str]]:
        """Yield one (feature_vector, label) pair per sample.

        Yields:
            A tuple of:
                - feature_vector: 1-D float32 array of shape (234,)
                - label: non-empty Polish sign label string (e.g. ``"A"``)
        """
        ...
