#!/usr/bin/env python3
"""Deez local MCP server.

Speaks MCP over stdio with Content-Length framing (and newline-JSON fallback).
Textbook two-body helpers only. Not a flight propagator.
"""

from __future__ import annotations

import json
import math
import re
import sys
from typing import Any

PROTOCOL = "2024-11-05"
SERVER_NAME = "deez"
SERVER_VERSION = "0.1.0"

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


def ok(req_id: Any, result: Any) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def err(req_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}


def circular_velocity(radius_m: float, mu: float = MU_EARTH_M3_S2) -> float:
    if radius_m <= 0:
        raise ValueError("radius_m must be positive")
    return math.sqrt(mu / radius_m)


def period_s(radius_m: float, mu: float = MU_EARTH_M3_S2) -> float:
    if radius_m <= 0:
        raise ValueError("radius_m must be positive")
    return 2.0 * math.pi * math.sqrt(radius_m**3 / mu)


def hohmann(r1_m: float, r2_m: float, mu: float = MU_EARTH_M3_S2) -> dict[str, float]:
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
        "mu_m3_s2": mu,
        "model": "ideal two-body Hohmann, spherical Earth, no drag, no J2",
    }


def altitude_to_radius(alt_m: float) -> float:
    return R_EARTH_M + alt_m


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


TOOLS = [
    {
        "name": "circular_orbit",
        "description": "Ideal two-body circular orbit period and speed from radius or altitude above WGS-84 equatorial radius.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "radius_m": {"type": "number", "description": "Orbit radius from Earth center in meters"},
                "altitude_m": {"type": "number", "description": "Altitude above 6378137 m equatorial radius"},
                "mu_m3_s2": {"type": "number", "description": "Gravitational parameter. Default Earth MU."},
            },
        },
    },
    {
        "name": "hohmann_transfer",
        "description": "Ideal two-body Hohmann delta-v and transfer time between two circular radii or altitudes.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "r1_m": {"type": "number"},
                "r2_m": {"type": "number"},
                "alt1_m": {"type": "number"},
                "alt2_m": {"type": "number"},
                "mu_m3_s2": {"type": "number"},
                "claimed_dv_m_s": {
                    "type": "number",
                    "description": "Optional claimed total delta-v to compare against the closed form",
                },
                "tolerance_m_s": {"type": "number", "description": "Pass band for claimed_dv_m_s. Default 1.0"},
            },
        },
    },
    {
        "name": "unit_audit",
        "description": "Scan text for mixed km/m, deg/rad, and km/s vs m/s.",
        "inputSchema": {
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        },
    },
    {
        "name": "keyword_gate",
        "description": "Coarse scan for handling keywords such as ITAR, EAR, classified. Heuristic only.",
        "inputSchema": {
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        },
    },
]


def call_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    mu = float(arguments.get("mu_m3_s2") or MU_EARTH_M3_S2)
    if name == "circular_orbit":
        if arguments.get("radius_m") is not None:
            r = float(arguments["radius_m"])
        elif arguments.get("altitude_m") is not None:
            r = altitude_to_radius(float(arguments["altitude_m"]))
        else:
            raise ValueError("provide radius_m or altitude_m")
        p = period_s(r, mu)
        v = circular_velocity(r, mu)
        return {
            "radius_m": r,
            "altitude_m": r - R_EARTH_M,
            "period_s": p,
            "period_min": p / 60.0,
            "speed_m_s": v,
            "mu_m3_s2": mu,
            "model": "ideal two-body circular, spherical Earth",
        }
    if name == "hohmann_transfer":
        if arguments.get("r1_m") is not None and arguments.get("r2_m") is not None:
            r1 = float(arguments["r1_m"])
            r2 = float(arguments["r2_m"])
        elif arguments.get("alt1_m") is not None and arguments.get("alt2_m") is not None:
            r1 = altitude_to_radius(float(arguments["alt1_m"]))
            r2 = altitude_to_radius(float(arguments["alt2_m"]))
        else:
            raise ValueError("provide r1_m and r2_m, or alt1_m and alt2_m")
        result = hohmann(r1, r2, mu)
        claimed = arguments.get("claimed_dv_m_s")
        if claimed is not None:
            tol = float(arguments.get("tolerance_m_s") or 1.0)
            delta = abs(float(claimed) - result["delta_v_total_m_s"])
            result["claimed_dv_m_s"] = float(claimed)
            result["residual_m_s"] = delta
            result["pass"] = delta <= tol
            result["tolerance_m_s"] = tol
        return result
    if name == "unit_audit":
        return unit_audit(str(arguments.get("text") or ""))
    if name == "keyword_gate":
        return keyword_gate(str(arguments.get("text") or ""))
    raise ValueError(f"unknown tool {name}")


def handle(msg: dict[str, Any]) -> dict[str, Any] | None:
    method = msg.get("method")
    req_id = msg.get("id")
    params = msg.get("params") or {}
    if method == "initialize":
        return ok(
            req_id,
            {
                "protocolVersion": PROTOCOL,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            },
        )
    if method == "notifications/initialized":
        return None
    if method == "tools/list":
        return ok(req_id, {"tools": TOOLS})
    if method == "tools/call":
        name = params.get("name")
        arguments = params.get("arguments") or {}
        try:
            result = call_tool(name, arguments)
            return ok(
                req_id,
                {
                    "content": [{"type": "text", "text": json.dumps(result, indent=2)}],
                    "structuredContent": result,
                    "isError": False,
                },
            )
        except Exception as exc:  # noqa: BLE001
            return ok(
                req_id,
                {
                    "content": [{"type": "text", "text": str(exc)}],
                    "isError": True,
                },
            )
    if method == "ping":
        return ok(req_id, {})
    if req_id is None:
        return None
    return err(req_id, -32601, f"method not found: {method}")


def write_message(msg: dict[str, Any]) -> None:
    body = json.dumps(msg, separators=(",", ":")).encode("utf-8")
    header = f"Content-Length: {len(body)}\r\n\r\n".encode("ascii")
    sys.stdout.buffer.write(header + body)
    sys.stdout.buffer.flush()


def read_stdio_messages():
    buf = b""
    while True:
        chunk = sys.stdin.buffer.read(1)
        if not chunk:
            if buf.strip():
                try:
                    yield json.loads(buf.decode("utf-8"))
                except json.JSONDecodeError:
                    pass
            return
        buf += chunk
        while True:
            if buf.startswith(b"{"):
                nl = buf.find(b"\n")
                if nl < 0:
                    break
                line = buf[:nl].decode("utf-8").strip()
                buf = buf[nl + 1 :]
                if line:
                    yield json.loads(line)
                continue
            header_end = buf.find(b"\r\n\r\n")
            if header_end < 0:
                header_end = buf.find(b"\n\n")
                sep_len = 2 if header_end >= 0 else 0
            else:
                sep_len = 4
            if header_end < 0:
                break
            header = buf[:header_end].decode("ascii", errors="replace")
            length = None
            for raw_line in header.splitlines():
                if raw_line.lower().startswith("content-length:"):
                    length = int(raw_line.split(":", 1)[1].strip())
            if length is None:
                buf = buf[header_end + sep_len :]
                continue
            start = header_end + sep_len
            if len(buf) < start + length:
                break
            body = buf[start : start + length]
            buf = buf[start + length :]
            yield json.loads(body.decode("utf-8"))


def main() -> None:
    for msg in read_stdio_messages():
        reply = handle(msg)
        if reply is not None:
            write_message(reply)


if __name__ == "__main__":
    main()
