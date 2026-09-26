---
name: gnc-skeleton
description: Scaffold a deterministic GNC cyclic task with bounded storage, separate estimate-guide-control steps, telemetry record, and a numeric check hook. Use when the user wants onboard GNC structure, a flight loop, or a control cycle skeleton.
---

# GNC skeleton

Generate structure, not a secret guidance law.

## Default shape

- Fixed-rate task. Explicit dt. No hidden threads on the control path.
- Three steps the user can merge if they insist: estimate, guide, control.
- Inputs and outputs are plain structs with units in comments.
- Storage is static or caller-owned.
- Telemetry is a fixed-size record.
- A hook calls out to a numeric check (Deez MCP or the repo's propagator) in tests, not in the flight cycle.

## Refuse

Do not invent vehicle-specific gains, TVC schedules, or proprietary autopilots.
If the user does not supply plant parameters, leave TODOs with unit annotations.

## Checklist after generation

- Units on every field
- Frame named on every vector
- No unbounded allocation in the cycle
- A test file exists
