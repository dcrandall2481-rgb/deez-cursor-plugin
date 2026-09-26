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

The MCP is an ideal two-body kernel. No drag, no J2, no SGP4. Pair it with [astrodynamics-mcp](https://github.com/astro-tools/astrodynamics-mcp) if you need propagation.

## Install in Cursor (activate now)

Until the public marketplace listing is approved, load it locally:

```bash
git clone https://github.com/dcrandall2481-rgb/deez-cursor-plugin.git ~/.cursor/plugins/local/deez
```

Reload the window (`Developer: Reload Window`). Enable **Deez** under Customize → Plugins. Confirm the `deez` MCP server is on and that `python3` is on PATH.

Or add the repo as a team/user marketplace source after you fork it.

## Marketplace

Public listing requires Cursor's manual review.

1. Repo (this one, must stay public): https://github.com/dcrandall2481-rgb/deez-cursor-plugin
2. Submit at https://cursor.com/marketplace/publish
3. After approval, install with `/add-plugin deez` from the Cursor marketplace.

## Try it

- "Hohmann from 400 km to 35786 km. Use Deez MCP. Quote the JSON."
- `/deez-review` on a GNC diff
- "Scaffold a cFS housekeeping app stub"

## Limits

- Keyword gate is not legal advice and not an audit control.
- Hohmann and circular-orbit tools are teaching-grade closed forms.
- Do not put export-controlled technical data in issues, cloud-agent prompts, or this public repo.

## License

MIT
