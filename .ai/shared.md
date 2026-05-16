# SHARED CONTEXT: pjm-translator

LEGEND:
  RPA   = Research → Plan → Act workflow (.ai/workflows/research-plan-act.md)
  GATE  = critical action requiring explicit user approval before execution
  LOW   = low-risk action (no approval needed)
  CRIT  = critical-risk action (GATE required)
  DI    = dependency inversion via Protocol / ABC
  AAA   = Arrange – Act – Assert test pattern
  PKG   = pyproject.toml + uv.lock

PROJECT:
  name:    pjm-translator
  purpose: real-time PJM (Polish Sign Language) → Polish translation
  stage:   early scaffold — src/ and tests/ do not exist yet
  dataset: https://www.kaggle.com/datasets/adamlaput/sign-language-pjm

STACK:
  language:  Python 3.14
  pkg-mgr:   uv (PEP 621, pyproject.toml / uv.lock)
  runtime:   numpy >= 2.4.4
  ml-stack:  not yet declared (OpenCV / MediaPipe / PyTorch / TF expected)
  ci-cd:     GitHub Actions (.github/workflows/ — both files are stubs)
  tests:     pytest + pytest-cov (planned, not yet configured)

ARCH:
  main.py              → thin entrypoint; delegates to src/
  src/                 → core importable package (train, inference, pipeline)
  data/                → exploration scripts; NOT imported by src/
  tests/               → pytest suite; mirrors src/ layout
  .github/workflows/   → ci.yaml (lint/test) + train.yaml (MLOps)

NAMING:
  variables / functions / modules / files → snake_case
  classes                                 → PascalCase
  constants                               → UPPER_SNAKE_CASE

FRAME_SCHEMA:
  type:  numpy.ndarray  dtype=uint8
  shape: (T, H, W, C)
  T = frame count  |  H = height px  |  W = width px  |  C = channels (3=RGB)

GATES — CRIT actions (always require user approval):
  - add / upgrade / remove packages in PKG
  - delete files or directories
  - modify .github/workflows/ files
  - change public function / API signatures that have existing callers
  - large refactor spanning ≥ 3 modules simultaneously
  - modify infrastructure / deployment configuration
  - overwrite existing configuration files
  - any irreversible operation

LOW — allowed without approval:
  - isolated bug fix with no external callers
  - code cleanup / style fix without behaviour change
  - add / improve comments or docstrings
  - add tests for existing functionality
  - new isolated feature in a new file (no existing code affected)
  - update documentation files only

CONTEXT_FILES:
  .ai/shared.md                      → common definitions (this file)
  .ai/context/project.md             → full project context
  .ai/workflows/research-plan-act.md → RPA workflow
  .ai/standards/coding.md            → coding standards
  .ai/standards/testing.md           → testing standards
  .ai/agents/developer.md            → developer agent
  .ai/agents/reviewer.md             → reviewer agent
  .ai/agents/mlops.md                → MLOps agent
  .ai/agents/data-engineer.md        → data engineer agent
