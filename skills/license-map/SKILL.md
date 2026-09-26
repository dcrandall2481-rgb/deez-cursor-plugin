---
name: license-map
description: Map a software change to a short licensing and trajectory-assumption checklist. Use when the user mentions FAA Part 450, FCC payload filings, licensed trajectory, RF license, range safety products, or asks whether a code change touches a licensed envelope.
---

# License map

This is a checklist generator, not legal practice.

## Questions to answer from the diff

1. Does the change alter planned delta-v, burn epoch, or target orbit?
2. Does it alter radio frequency, bandwidth, or pointing used for comms?
3. Does it alter a destruct, inhibit, or range-safety interface?
4. Does it alter public reporting (orbital data, conjunction process)?

## Output format

- Touched / not touched / unknown for each question
- Files that drove the call
- What evidence would close an unknown

Do not draft a license application unless the user supplies the program's real template.
Do not cite invented docket numbers.
