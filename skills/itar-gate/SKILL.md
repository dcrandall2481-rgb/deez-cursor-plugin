---
name: itar-gate
description: Heuristic handling gate before sending aerospace text to a cloud agent. Use when the user mentions ITAR, EAR, CMMC, classified, export control, air-gap, or asks whether a file should stay local.
---

# Handling gate

1. Run Deez MCP `keyword_gate` on the text or diff.
2. If any hit, recommend local/offline agent mode and do not paste the body into a cloud prompt.
3. Remind the user the scan is a keyword heuristic. Counsel and the program security officer decide.

## Do not

- Classify documents.
- Extract or rewrite suspected controlled technical data into a cleaner form for the cloud.
- Claim this gate satisfies a compliance audit.
