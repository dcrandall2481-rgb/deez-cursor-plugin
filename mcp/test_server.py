#!/usr/bin/env python3
"""Sanity checks for Deez two-body helpers."""

from server import circular_velocity, hohmann, keyword_gate, period_s, unit_audit

R_EARTH = 6378137.0


def near(a: float, b: float, tol: float) -> None:
    assert abs(a - b) <= tol, (a, b, tol)


def test_leo_period() -> None:
    r = R_EARTH + 400_000.0
    p = period_s(r)
    near(p / 60.0, 92.56, 0.5)
    v = circular_velocity(r)
    near(v, 7670.0, 20.0)


def test_geo_hohmann() -> None:
    r1 = R_EARTH + 400_000.0
    r2 = R_EARTH + 35_786_000.0
    out = hohmann(r1, r2)
    near(out["delta_v_total_m_s"], 3930.0, 80.0)


def test_unit_audit() -> None:
    result = unit_audit("burn 100 m/s then 0.1 km/s")
    assert result["ok"] is False


def test_keyword_gate() -> None:
    result = keyword_gate("This memo is ITAR marked.")
    assert result["action"] == "keep_local"


if __name__ == "__main__":
    test_leo_period()
    test_geo_hohmann()
    test_unit_audit()
    test_keyword_gate()
    print("ok")
