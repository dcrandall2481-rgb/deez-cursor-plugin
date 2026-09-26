---
name: cfs-fprime
description: Scaffold NASA cFS or F Prime style component stubs, message dictionaries, and interface comments. Use when the user mentions cFS, core Flight System, F Prime, F', flight software component, or CCSDS-style telemetry packets at the software-architecture level.
---

# cFS / F Prime stubs

Stay at public framework shape.

## cFS

- App with init, cyclic pipe read, and cleanup.
- Software Bus message IDs as named constants the user must assign.
- Housekeeping packet with a sequence counter and a bounded table of channels.
- Do not copy internal NASA mission tables.

## F Prime

- Component with ports listed in comments or a stub XML/Ai if the repo already uses that layout.
- Commands and telemetry channels named, types explicit, no secret opcodes.

## Always

Ask which framework if the user did not say. Do not mix cFS macros into an F Prime tree.
Add a note that this is not a flight-qualification kit.
