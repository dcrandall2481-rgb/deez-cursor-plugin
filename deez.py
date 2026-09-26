#!/usr/bin/env python3
"""Deez CLI — same two-body kernel as the Cursor plugin MCP."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from typing import Any

MU_EARTH_M3_S2 = 3.986004418e14
R_EARTH_M = 6378137.0

KEYWORD_FLAGS = [
    (r"\bitar\b", "Document mentions ITAR. Keep work local unless counsel says otherwise."),
    (r"\bexport administration regulation", "Document mentions EAR. Confirm classification before sending to a cloud agent."),
    (r"\bear\s+controlled\b", "Document mentions EAR-controlled material. Confirm handling before a cloud agent."),
    (r"\bclassified\b", "Classification language present. Do not send this file to a vendor cloud."),
    (r"\bcmmc\b", "CMMC language present. Follow the program's handling rules."),
    (r"\bexport[\s-]?control", "Export-control language present."),
]


def circular_velocity(radius_m: float, mu: float = MU_EARTH_M3_S2) -> float:
    if radius_m <= 0:
        raise ValueError("radius_m must be positive")
    return math.sqrt(mu / radius_m)


def period_s(radius_m: float, mu: float = MU_EARTH_M3_S2) -> float:
    if radius_m <= 0:
        raise ValueError("radius_m must be positive")
    return 2.0 * math.pi * math.sqrt(radius_m**3 / mu)


def hohmann(r1_m: float, r2_m: float, mu: float = MU_EARTH_M3_S2) -> dict[str, float | str]:
    if r1_m <= 0 or r2_m <= 0:
        raise ValueError("radii must be positive")
    a_t = 0.5 * (r1_m + r2_m)
    v1 = circular_velocity(r1_m, mu)
    v2 = circular_velocity(r2_m, mu)
    v_peri = math.sqrt(mu * (2.0 / r1_m - 1.0 / a_t))
    v_apo = math.sqrt(mu * (2.0 / r2_m - 1.0 / a_t))
    dv1 = abs(v_peri - v1)
    dv2 = abs(v2 - v_apo)
    tof = math.pi * math.sqrt(a_t**3 / mu)
    return {
        "r1_m": r1_m,
        "r2_m": r2_m,
        "semi_major_transfer_m": a_t,
        "v_circular_1_m_s": v1,
        "v_circular_2_m_s": v2,
        "delta_v_1_m_s": dv1,
        "delta_v_2_m_s": dv2,
        "delta_v_total_m_s": dv1 + dv2,
        "time_of_flight_s": tof,
        "time_of_flight_h": tof / 3600.0,
        "mu_m3_s2": mu,
        "model": "ideal two-body Hohmann, spherical Earth, no drag, no J2",
    }


def circular_orbit(altitude_km: float) -> dict[str, float | str]:
    r = R_EARTH_M + altitude_km * 1000.0
    p = period_s(r)
    v = circular_velocity(r)
    return {
        "radius_m": r,
        "altitude_m": altitude_km * 1000.0,
        "period_s": p,
        "period_min": p / 60.0,
        "speed_m_s": v,
        "mu_m3_s2": MU_EARTH_M3_S2,
        "model": "ideal two-body circular, spherical Earth",
    }


UNIT_PATTERNS = [
    ("km", re.compile(r"\b\d+(?:\.\d+)?\s*km\b", re.I)),
    ("m", re.compile(r"\b\d+(?:\.\d+)?\s*m\b", re.I)),
    ("deg", re.compile(r"\b\d+(?:\.\d+)?\s*deg(?:rees)?\b", re.I)),
    ("rad", re.compile(r"\b\d+(?:\.\d+)?\s*rad(?:ians)?\b", re.I)),
    ("km/s", re.compile(r"\b\d+(?:\.\d+)?\s*km/s\b", re.I)),
    ("m/s", re.compile(r"\b\d+(?:\.\d+)?\s*m/s\b", re.I)),
]


def unit_audit(text: str) -> dict[str, Any]:
    found: dict[str, int] = {}
    for label, pat in UNIT_PATTERNS:
        n = len(pat.findall(text))
        if n:
            found[label] = n
    warnings = []
    if found.get("km") and found.get("m"):
        warnings.append("Text mixes km and m. Convert at one boundary and keep SI internally.")
    if found.get("deg") and found.get("rad"):
        warnings.append("Text mixes degrees and radians. Keep radians in kernels.")
    if found.get("km/s") and found.get("m/s"):
        warnings.append("Text mixes km/s and m/s.")
    return {"counts": found, "warnings": warnings, "ok": len(warnings) == 0}


def keyword_gate(text: str) -> dict[str, Any]:
    hits = []
    for pat, note in KEYWORD_FLAGS:
        if re.search(pat, text, flags=re.I):
            hits.append({"pattern": pat, "note": note})
    return {
        "hits": hits,
        "action": "keep_local" if hits else "no_flag",
        "disclaimer": "Heuristic only. Not legal advice. Does not detect actual controlled technical data.",
    }


def dump(obj: Any) -> None:
    print(json.dumps(obj, indent=2))


def main() -> int:
    p = argparse.ArgumentParser(description="Deez two-body console (not official SpaceX software)")
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("circular", help="circular orbit from altitude km")
    c.add_argument("--alt-km", type=float, default=400.0)

    h = sub.add_parser("hohmann", help="Hohmann between two altitudes km")
    h.add_argument("--alt1-km", type=float, default=400.0)
    h.add_argument("--alt2-km", type=float, default=35786.0)

    u = sub.add_parser("units", help="scan text for mixed units")
    u.add_argument("text")

    g = sub.add_parser("gate", help="scan text for handling keywords")
    g.add_argument("text")

    s = sub.add_parser("smoke", help="run the v0.1 live stamp cases")

    args = p.parse_args()
    if args.cmd == "circular":
        dump(circular_orbit(args.alt_km))
    elif args.cmd == "hohmann":
        dump(hohmann(R_EARTH_M + args.alt1_km * 1000.0, R_EARTH_M + args.alt2_km * 1000.0))
    elif args.cmd == "units":
        dump(unit_audit(args.text))
    elif args.cmd == "gate":
        dump(keyword_gate(args.text))
    elif args.cmd == "smoke":
        dump(
            {
                "circular_400km": circular_orbit(400.0),
                "hohmann_400_to_35786": hohmann(R_EARTH_M + 400_000.0, R_EARTH_M + 35_786_000.0),
                "unit_audit": unit_audit("delta-v 3.85 km/s then 7668.6 m/s at 400 km"),
                "keyword_gate": keyword_gate("ITAR memo mixed with unclassified cubesat ICD"),
            }
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
