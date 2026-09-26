---
name: orbit-check
description: Verify orbit and maneuver numbers with the Deez MCP instead of model memory. Use when the user asks for period, circular speed, Hohmann delta-v, or wants a test fixture that locks a claimed burn against a closed form.
---

# Orbit check

## Do this

1. Collect inputs with units. Convert to meters and seconds before any tool call.
2. Call Deez MCP `circular_orbit` or `hohmann_transfer`.
3. Quote the tool JSON in the reply. Label the model (ideal two-body).
4. If the user already claimed a delta-v, pass `claimed_dv_m_s` and report pass/fail.
5. When generating code, add a unit test that encodes the same inputs and asserts the residual.

## Do not do this

- Do not recall LEO speed from training and stop there.
- Do not use SGP4, drag, or J2 unless a separate propagator MCP is installed. Say the model limit.
- Do not present Hohmann numbers as a flight design.

## Test shape

```python
def test_hohmann_fixture():
    # values must match the MCP output that produced this PR
    claimed = 3932.0  # m/s, replace with tool result
    assert abs(claimed - 3932.0) < 1.0
```

Replace the fixture with the actual tool output. Prefer calling a small helper the repo owns over hard-coding if the user already has one.
