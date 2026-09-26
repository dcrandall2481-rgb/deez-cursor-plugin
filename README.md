# Deez

Cursor plugin for space-engineering software work.

Deez is not an official SpaceX, SpaceXAI, NASA, or USAF product. It does not expose internal vehicle data. It binds the agent to public textbook two-body math, high-reliability coding habits, and a handling-keyword gate.

## What you get

| Piece | Role |
| --- | --- |
| Rules | Units/frames, flight-path hygiene, "do not invent numbers" |
| Skills | orbit-check, gnc-skeleton, cfs-fprime, conjunct, license-map, itar-gate |
| Commands | `/deez-review`, `/deez-orbit` |
| Agent | `deez-reviewer` |
| MCP | Local `python3` server: circular orbit, Hohmann check, unit audit, keyword gate |
| CLI | `python3 deez.py smoke` — same kernel, executed outside Cursor |
| Console | `console/index.html` — browser-executable live console |

The MCP is an ideal two-body kernel. No drag, no J2, no SGP4. Pair it with [astrodynamics-mcp](https://github.com/astro-tools/astrodynamics-mcp) if you need propagation.

## Run it live (no Cursor required)

```bash
python3 deez.py smoke
python3 deez.py hohmann --alt1-km 400 --alt2-km 35786
python3 mcp/test_server.py
```

Open `console/index.html` in a browser. It auto-executes the 400 km circular case and the 400 km → 35,786 km Hohmann case.

Reference stamp (this kernel):

- Circular 400 km: period 92.56 min, speed 7,668.56 m/s
- Hohmann 400 → 35,786 km: Δv 3,853.96 m/s, time of flight 5.29 h

## Install in Cursor (activate now)

Until the public marketplace listing is approved, load it locally:

```bash
git clone https://github.com/dcrandall2481-rgb/deez-cursor-plugin.git ~/.cursor/plugins/local/deez
```

Reload the window (`Developer: Reload Window`). Enable **Deez** under Customize → Plugins. Confirm the `deez` MCP server is on and that `python3` is on PATH.

## Marketplace

Public listing requires Cursor's manual review.

1. Repo (this one, must stay public): https://github.com/dcrandall2481-rgb/deez-cursor-plugin
2. Submit at https://cursor.com/marketplace/publish
3. After approval, install with `/add-plugin deez` from the Cursor marketplace.

## Limits

- Keyword gate is not legal advice and not an audit control.
- Hohmann and circular-orbit tools are teaching-grade closed forms.
- Do not put export-controlled technical data in issues, cloud-agent prompts, or this public repo.

## License

MIT
