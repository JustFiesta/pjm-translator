# AGENTS.md — sign-language-translator

Real-time ASL (American Sign Language) hand sign classifier.
Detects the hand region via webcam using MediaPipe, crops and resizes it to
a 28×28 grayscale image, and classifies it with a scikit-learn SVC trained on
the Sign Language MNIST dataset.  Recognised letter is displayed on-screen.

Dataset source: [Sign Language MNIST on Kaggle](https://www.kaggle.com/datasets/datamunge/sign-language-mnist)  
Authors: Matthew & Kacper  
Python: 3.14 · Package manager: uv

---

## Repository layout

```
pjm-translator/
├── data/
│   ├── raw/                        # Source CSVs — read-only, do NOT modify
│   │   ├── sign_mnist_train.csv    # Training set (27 455 samples, 24 classes)
│   │   ├── sign_mnist_test.csv     # Held-out test set (7 172 samples)
│   │   └── amer_sign*.png          # Reference images (not used in training)
│   └── processed/                  # Generated splits/features; gitignored
├── artifacts/                      # Trained model files (.pkl); gitignored locally
├── src/
│   ├── data/                  # Ingest, feature extraction, train/val/test split
│   │   ├── ingest.py          # Load raw CSV → DataFrame, normalise pixels
│   │   ├── extract.py         # Build feature matrix from DatasetSource
│   │   ├── split.py           # Stratified 80/10/10 split by label
│   │   └── protocol.py        # DatasetSource Protocol
│   ├── model/                 # Training and evaluation
│   │   ├── train.py           # Fit sklearn classifier, save to artifacts/
│   │   └── evaluate.py        # Metrics (accuracy, per-class report)
│   └── inference/             # Real-time prediction pipeline
│       ├── camera.py          # Webcam capture + MediaPipe bbox → 28×28 crop
│       ├── csv_source.py      # Offline FeatureSource from CSV row
│       ├── predict.py         # Load model, run inference on live feature vector
│       └── protocol.py        # FeatureSource Protocol
├── tests/                     # pytest tests, mirror src/ layout
│   ├── conftest.py            # Shared fixtures and fake data factories
│   ├── data/
│   │   ├── test_ingest.py
│   │   ├── test_extract.py
│   │   └── test_split.py
│   ├── model/
│   │   └── test_train.py
│   └── inference/
│       └── test_predict.py
├── main.py                    # Thin entrypoint — wires src/ modules, no logic
├── pyproject.toml             # uv-managed; GATE approval required to modify
├── doc/
│   └── dev-setup.md           # Developer environment setup guide
└── .github/workflows/
    ├── ci.yaml                # Ruff lint + pytest + build (every push / PR)
    └── train.yaml             # Manual dispatch; trains model, uploads artifact
```

---

## Data schema

Primary training file: `data/raw/sign_mnist_train.csv`.

| Column | Type | Description |
|--------|------|-------------|
| `label` | int | **Target class** — integer 0–24 mapping to letters A–Y (no J=9, no Z=25) |
| `pixel1` … `pixel784` | int (0–255) | Flattened 28×28 grayscale hand image |

**Label → letter**: `chr(ord('A') + label)` — e.g. 0→'A', 1→'B', 10→'K'.  
**Feature vector**: **784 numeric columns** per sample, normalised to `[0, 1]`.  
**Train / val / test split**: 80 / 10 / 10, stratified by `label`.

---

## Environment setup

```shell
uv python install 3.14
uv venv --python 3.14

# Windows PowerShell
.venv\Scripts\Activate.ps1

# Linux / macOS
source .venv/bin/activate

uv sync
```

---

## Essential commands

| Task | Command |
|------|---------|
| Run app | `uv run python main.py` |
| Run tests | `uv run pytest` |
| Run tests + coverage | `uv run pytest --cov=src --cov-report=term-missing` |
| Lint | `uv run ruff check src/ tests/` |
| Format | `uv run ruff format src/ tests/` |
| Train model (local) | `uv run python -m src.model.train` |
| Live inference | `uv run python main.py infer --source camera` |
| CSV inference (one row) | `uv run python main.py infer --source csv --row 0` |

---

## Architecture

```
Webcam
  │
  ▼
MediaPipe HandLandmarker          src/inference/camera.py
  │  (bounding box of detected hand)
  ▼
Crop + resize 28×28 + grayscale   src/inference/camera.py
  │
  ▼
Flatten → 784-dim vector [0,1]    src/inference/camera.py
  │
  ├──[training]──▶ sklearn SVC ──▶ artifacts/model.pkl
  │                src/model/train.py
  │                (trained on sign_mnist_train.csv — same 784-dim format)
  │
  └──[inference]─▶ artifacts/model.pkl ──▶ letter (str)
                   src/inference/predict.py
                         │
                         ▼
                   CLI output + OpenCV overlay
                   main.py
```

Training is fully offline (Sign Language MNIST CSV).  Inference reuses the identical
784-dim image pipeline on live webcam output — train and inference feature spaces match.

---

## Coding conventions

- **Naming**: `snake_case` functions / files / variables · `PascalCase` classes · `UPPER_SNAKE` constants.
- **Type hints**: required on every public function signature — no exceptions.
- **Docstrings**: Google-style on every public function and class.
- **Line length**: 88 characters (enforced by Ruff).
- **`main.py`**: thin entrypoint only — all logic lives in `src/`.
- **Interfaces**: use `Protocol` for dependency inversion; wire at `main.py` boundary.
- **Comments**: explain **why**, never what. No narration comments.
- **TODO comments**: must not appear in delivered code.

---

## Testing

- Mirror `src/` layout under `tests/` (e.g. `src/data/ingest.py` → `tests/data/test_ingest.py`).
- Shared fixtures and synthetic data factories go in `tests/conftest.py`.
- Every test function must cover at least one happy-path case and one edge/error case.
- Do **not** commit code that breaks `uv run pytest`.
- CI runs the full suite — keep it green at all times.

---

## Model artifacts

| Context | Location | Notes |
|---------|----------|-------|
| Local dev | `artifacts/model.pkl` | Gitignored; generated by `src/model/train.py` |
| CI / production | GitHub Actions artifact | Uploaded by `train.yaml` manual dispatch |

Serialisation format: `joblib` pickle (`.pkl`).  
Preferred classifiers to try first: `SVC` (RBF kernel), `RandomForestClassifier`.

---

## PR and commit conventions

- **Commit style**: imperative English, ≤72 characters.  
  Examples: `Add feature extraction for 550-points dataset`, `Fix stratified split edge case`
- **Before opening a PR**: run `uv run ruff check src/ tests/` and `uv run pytest` — both must pass.
- **CI**: all checks in `ci.yaml` must be green before merge.
- **PR title**: concise imperative summary matching the commit style.

---

## GATE operations — require explicit user approval before execution

The following actions must **not** be taken autonomously:

- Adding, upgrading, or removing any package in `pyproject.toml`
- Deleting any file or directory
- Modifying `.github/workflows/` files
- Changing a public function signature that has existing callers
- Refactoring spanning ≥ 3 modules simultaneously
- Any irreversible operation (data deletion, force-push, etc.)

Present the proposed change and wait for explicit "yes / proceed" before acting.

---

## Security notes

- Never commit `data/raw/*.csv` files if they contain sensitive user data — verify before push.
- Never commit model artifacts (`artifacts/`) — covered by `.gitignore`.
- Never commit `.env` files or any credentials.
- `data/processed/` is gitignored — do not force-add it.
