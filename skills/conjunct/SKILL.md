---
name: conjunct
description: Screen conjunction language and miss-distance math at a software level. Use when the user asks about close approaches, conjunction screening, collision avoidance software, or comparing two Keplerian states. Does not replace 18 SPCS, TraCSS, or an operational SSA provider.
---

# Conjunction hygiene

## Allowed

- Help structure a screening job: two states, one epoch, one frame, one miss-distance definition.
- Convert units. Refuse to mix km and m.
- If only TLEs are available and no SGP4 MCP is installed, say you cannot propagate and stop.
- If astrodynamics-mcp or another propagator is connected, use that for geometry. Deez MCP is two-body circular/Hohmann only.

## Not allowed

- Do not produce an operational conjunction data message that pretends to be 18 SPCS.
- Do not recommend a debris-creating burn.
- Do not fabricate covariance.

## Output

Name frame, time scale, and model. If the geometry is incomplete, list missing fields instead of filling them.
