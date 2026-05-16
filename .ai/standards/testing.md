# STANDARDS: Testing

IMPORT: .ai/shared.md

STATUS: pytest / pytest-cov not yet configured.
        MUST NOT add as deps without GATE approval.
        Write tests that would pass once configured.

---

[FRAMEWORK]
  runner:   pytest
  coverage: pytest-cov
  run:      uv run pytest
  coverage: uv run pytest --cov=src --cov-report=term-missing

---

[LAYOUT]
`tests/` mirrors `src/`:

```
tests/
├── __init__.py
├── conftest.py            ← shared fixtures
├── test_pipeline.py       ← tests for src/pipeline.py
├── test_train.py          ← tests for src/train.py
└── data/                  ← small fixture files (NOT the real dataset)
    └── sample_frames.npy
```

- MUST have one `test_<module>.py` per `src/<module>.py`
- MUST NOT place test files inside `src/`

---

[NAMING]
  files:     `test_<module_name>.py`
  functions: `test_<what_is_being_tested>`
  fixtures:  descriptive noun — `sample_frames`, `mock_classifier`

```python
def test_classify_sign_returns_label_above_threshold(): ...
def test_classify_sign_returns_empty_string_below_threshold(): ...
def test_load_frames_raises_on_missing_file(): ...
```

---

[STRUCTURE — AAA]
```python
def test_classify_sign_returns_label_above_threshold(sample_frames):
    # Arrange
    classifier = SignClassifier(threshold=0.5)
    # Act
    result = classifier.classify(sample_frames)
    # Assert
    assert isinstance(result, str)
    assert len(result) > 0
```

---

[FIXTURES]
- MUST define reusable fixtures in `tests/conftest.py`
- MUST use small synthetic data; MUST NOT load the real Kaggle dataset
- MUST mock heavy ML models

```python
@pytest.fixture
def sample_frames() -> np.ndarray:
    return np.zeros((4, 64, 64, 3), dtype=np.uint8)  # (T, H, W, C)
```

---

[COVERAGE TARGETS]
  src/ overall          → 80%
  critical inference    → 95%
  data utilities        → 70%

---

[WHAT TO TEST]
  MUST test:
    - happy-path of every public function
    - edge cases: empty inputs, boundary values, max sizes
    - error paths: ValueError / RuntimeError raised with correct messages

  MUST NOT test:
    - Python built-in behaviour
    - implementation details that may change without affecting public behaviour
    - trained model weights or large binary assets

---

[ML-SPECIFIC]
- MUST use small synthetic tensors/arrays; MUST NOT use real dataset
- Separate unit tests (fast, no GPU, no I/O) from integration tests
- MUST mark slow / GPU tests: `@pytest.mark.slow`
- MUST NOT commit model checkpoint files

```python
@pytest.mark.slow
def test_full_training_loop(): ...
```

---

[COMMANDS]
  uv run pytest                                       ← all tests
  uv run pytest -m "not slow"                        ← fast only
  uv run pytest --cov=src --cov-report=term-missing  ← with coverage
  uv run pytest tests/test_pipeline.py -v            ← single file
