# Measured 2026-09-20 — commands behind every number in resume.yaml

Run from `C:\AitherOS-Fresh` (branch `feat/tunnel-phone-coding`) unless noted.

| figure | command | result |
|---|---|---|
| commits total | `git rev-list --count HEAD` | 25247 |
| first commit | `git log --format=%ad --date=short --reverse \| head -1` | 2025-06-08 |
| commits 90d | `git rev-list --count --since='90 days ago' HEAD` | 16954 |
| tracked files | `git ls-files \| wc -l` | 35809 |
| compose services | `grep -cE '^  [a-z][a-z0-9-]+:$' .DEPLOYMENT/compose/docker-compose.aitheros.yml` | 378 |
| service modules | `find AitherOS/services -name 'Aither*.py' -maxdepth 2 \| wc -l` | 226 |
| quality gates | `git ls-files 'AitherOS/dev/tools/check_*.py' \| wc -l` | 960 |
| MCP tool modules | `ls AitherOS/apps/awnode/tools/mcp/mcp_*.py \| wc -l` | 263 |
| MCP tools served | gateway `tools/list` (CLAUDE.md records 1204–1211 on probe) | ~1,200 |
| blog posts | `ls AitherOS/apps/AitherVeil/content/blog/*.md \| wc -l` | 278 |
| routines | `ls AitherOS/config/routines/*.yaml \| wc -l` | 186 |
| agents | `ls .claude/agents \| wc -l` | 33 |
| aw* bricks | `python -c "...yaml.safe_load(ecosystem.yaml)['bricks']"` | 85 (public 63, planned 15, unpublished 4, no-pages 2, merged 1) |
| aw* stacks | same, `stacks` | 22 |
| org public repos | `gh repo list Aitherium --limit 200 --json visibility` | 78 public |
| PyPI | `curl https://pypi.org/pypi/<pkg>/json` | awdk 3.8.22, awgit 1.11.0, awgraph 1.4.8, awrelay 0.4.0; 51 brick ids on PyPI with Aitherium metadata |
| fleet-live lane | `.claude/rules/gates/1zA-*.md` | fleet-live 136; host-live 295; ci-static 504; selftest-only 34 (gate_lanes.yaml @ origin/develop) |
| ledger rate | `.claude/rules/tech-debt-ledger.md` | ~79 rows/day in vs ~4.2/day out (19 days measured, 2026-07) |
| verifier sites rotated | `.claude/rules/gates/1n-*.md` | 43 sites across 25 files |
| embedder | blog `code-search-embedder-13x-smaller-beats-its-teacher.md` | 13x smaller, beats teacher, $3 |

Counts taken 2026-09-20 on ref origin/develop (not the working tree, which drifts). MCP tools served, service modules and MCP tool modules were NOT re-measured (gateway was down).

USAF / Tanium / Boeing figures are from the owner's LinkedIn profile (2026-09-03 export) and were not re-measured here.
