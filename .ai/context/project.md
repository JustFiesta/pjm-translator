# CONTEXT: pjm-translator

IMPORT: .ai/shared.md

PURPOSE:
  Real-time PJM → Polish translation.
  Stage: early scaffold — main.py and data/explore.py are stubs; src/ not yet created.
  Dataset: https://www.kaggle.com/datasets/adamlaput/sign-language-pjm

STACK: → see SHARED.STACK
  future-deps (⚠️ GATE before adding any):
    - OpenCV / MediaPipe  → video capture + hand-landmark extraction
    - PyTorch / TensorFlow → model training + inference

ARCH: → see SHARED.ARCH
  current status:
    main.py            → stub (prints hello; TODO: delegate to src/)
    data/explore.py    → stub (single TODO comment)
    src/               → NOT YET CREATED
    tests/             → NOT YET CREATED
    .github/workflows/ → ci.yaml and train.yaml are single-line TODOs

CONVENTIONS:
  naming:      → see SHARED.NAMING
  entry_guard: if __name__ == "__main__": in every executable script
  imports:     stdlib → third-party → local (PEP 8)
  type_hints:  MUST on all public function signatures
  docstrings:  Google-style on all public functions and classes
  line_length: 88 chars (Black-compatible)
  formatter:   Black + Ruff (planned; not yet configured)

DEPS:
  numpy >= 2.4.4 → numerical arrays; foundation for future CV/ML work

DEV_SETUP:
  pip install uv
  uv sync
  uv run main.py
  → full instructions: doc/dev-setup.md
