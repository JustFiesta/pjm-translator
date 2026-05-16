# WORKFLOW: RPA (Research → Plan → Act)

IMPORT: .ai/shared.md

RULE: Execute all 3 phases in order. MUST NOT skip Research or Plan.

---

[RESEARCH]
GOAL:   Understand current state before writing any code.
STEPS:
1. List all files to read, create, or modify (include indirect deps)
2. Read every affected file in full
3. Map all imports + callers of every symbol you intend to change
4. Identify shared state, globals, import-time side effects
5. Classify risk: LOW or CRIT (→ SHARED.GATES / SHARED.LOW)
OUTPUT: risk classification (LOW | CRIT) + list of affected files

---

[PLAN]
GOAL:   Produce an ordered, user-approved implementation plan.
STEPS:
1. Decompose into smallest independently testable steps
2. Estimate: layers touched, file/line count, backward-compatibility
3. Identify what can go wrong at each step; note irreversible operations
4. Mark every CRIT step: ⚠️ GATE: <description>
5. Present ordered plan to user → MUST wait for explicit approval
OUTPUT: ordered step list with GATE markers

---

[ACT]
GOAL:   Implement the approved plan incrementally and safely.
STEPS:
1. Implement one step at a time
2. Validate (run `uv run pytest` / verify behaviour) before next step
3. Stop and report if unexpected findings arise
4. Re-confirm with user before every GATE action (even if already in plan)
5. Summarise each step: list changed file + one-line change description
OUTPUT: changed-files list + test result

---

CHECKLIST:
  Research: [ ] files listed  [ ] files read  [ ] deps mapped
            [ ] side-effects checked  [ ] risk classified
  Plan:     [ ] steps decomposed  [ ] impact estimated  [ ] risks listed
            [ ] GATEs flagged  [ ] user approved
  Act:      [ ] one-step-at-a-time  [ ] no unrelated changes  [ ] validated
            [ ] GATEs re-confirmed  [ ] summarised
