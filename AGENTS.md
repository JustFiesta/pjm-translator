# AGENTS.md — pjm-translator

Simple real-time translator from Polish Sign Language (PJM) to written Polish text.
Captures hand landmarks via webcam, classifies gestures with a scikit-learn
classifier trained on 3D keypoint data, and displays the recognised word on-screen (CLI/streamlit).

Dataset source: [sign-language-pjm on Kaggle](https://www.kaggle.com/datasets/adamlaput/sign-language-pjm)  
Authors: Matthew & Kacper  
Python: 3.14 · Package manager: uv

---

## Repository layout

```
pjm-translator/
├── data/
│   ├── raw/                   # Source CSVs — read-only, do NOT modify
│   │   ├── PJM-points.csv     # Full dataset (~2150 samples)
│   │   ├── 550-points.csv     # Dev subset (550 samples) ← primary for training
│   │   ├── 2150-points.csv    # Medium subset
│   │   └── *-images.csv       # Not used in v1
│   │   └── *-vectors.csv      # Not used in v1
│   └── processed/             # Generated splits/features; gitignored
├── artifacts/                 # Trained model files (.pkl); gitignored locally
├── src/
│   ├── data/                  # Ingest, feature extraction, train/val/test split
│   │   ├── ingest.py          # Load raw CSV → DataFrame
│   │   ├── extract.py         # Build 234-dim feature vector from point columns
│   │   └── split.py           # Stratified 80/10/10 split by sign_label
│   ├── model/                 # Training and evaluation
│   │   ├── train.py           # Fit sklearn classifier, save to artifacts/
│   │   └── evaluate.py        # Metrics (accuracy, per-class report)
│   └── inference/             # Real-time prediction pipeline
│       ├── camera.py          # Webcam capture + MediaPipe hand landmark extraction
│       └── predict.py         # Load model, run inference on live feature vector
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

Primary training file: `data/raw/550-points.csv` (dev), `data/raw/PJM-points.csv` (production).

| Column | Type | Description |
|--------|------|-------------|
| `user_id` | int | Recorder identifier — drop before training |
| `lux_value` | int | Lighting level (550 or 2150) — drop before training |
| `sign_label` | str | **Target class** — Polish letter/word (e.g. `"A"`) |
| `vector_hand_{1,2,3}_{x,y,z}` | float | Wrist orientation vector per hand (9 cols) |
| `point_{h}_{i}` (h=1..3, i=1..75) | float | 3D landmark coordinates per hand (225 cols) |

**Feature vector**: 9 (vectors) + 225 (points) = **234 numeric columns** per sample.  
**Train / val / test split**: 80 / 10 / 10, stratified by `sign_label`.

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
| Explore data | `uv run python data/explore.py` |

---

## Architecture

```
Webcam
  │
  ▼
MediaPipe HandLandmarker          src/inference/camera.py
  │  (21 landmarks × 3 hands × xyz)
  ▼
Feature extractor (234 dims)      src/data/extract.py
  │
  ├──[training]──▶ sklearn classifier ──▶ artifacts/model.pkl
  │                src/model/train.py
  │
  └──[inference]─▶ artifacts/model.pkl ──▶ sign_label (str)
                   src/inference/predict.py
                         │
                         ▼
                   Streamlit overlay / CLI output
                   main.py
```

Training is fully offline (CSV data). Inference reuses the identical 234-dim extractor
on live MediaPipe output so train/inference feature spaces are identical.

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
