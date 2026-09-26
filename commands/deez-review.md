---
name: deez-review
description: Review the current diff for units, frames, invented orbital numbers, flight-path allocation, and handling keywords.
---

Review the current uncommitted diff and nearby flight/GNC files.

1. Run Deez MCP `unit_audit` on changed text.
2. Run Deez MCP `keyword_gate` on changed text.
3. Flag any orbital number that did not come from a tool call or a fixture.
4. Flag unbounded allocation on cyclic/control paths.
5. Flag state vectors with no frame or time scale.
6. End with a punch list. Do not rewrite the whole tree unless asked.
