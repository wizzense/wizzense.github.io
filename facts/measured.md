# Measured 2026-10-05 — commands behind every number in resume.yaml

Run from `C:\AitherOS-Fresh` against `R=origin/develop` (never the working tree, which drifts).

| figure | command | result |
|---|---|---|
| commits total | `git rev-list --count $R` | 29340 |
| first commit | `git log --format=%ad --date=short --reverse $R \| head -1` | 2025-06-08 |
| commits 90d | `git rev-list --count --since='90 days ago' $R` | 20346 |
| merged PRs, total | `git log $R --format=%s \| grep -oE '\(#[0-9]+\)$' \| sort -u \| wc -l` | 4074 |
| merged PRs since 2026-09-20 | same, `--since=2026-09-20` | 2357 |
| feature PRs since 2026-09-20 | same, subjects starting `feat` | 746 |
| tracked files | `git ls-tree -r --name-only $R \| wc -l` | 40985 |
| compose services | `git show $R:.DEPLOYMENT/compose/docker-compose.aitheros.yml \| grep -cE '^  [a-z][a-z0-9-]+:$'` | 381 |
| service modules | `git ls-tree -r --name-only $R AitherOS/services \| grep -cE 'Aither[^/]*\.py$'` (top two levels) | 223 |
| quality gates | `git ls-tree -r --name-only $R AitherOS/dev/tools \| grep -cE '/check_[^/]*\.py$'` | 1144 |
| MCP tool modules | `git ls-tree -r --name-only $R AitherOS/apps/awnode/tools/mcp \| grep -cE '/mcp_[^/]*\.py$'` | 306 |
| MCP tools served | gateway `127.0.0.1:8182/mcp`: `initialize`, then `tools/list` (owner session) | 1703 |
| blog posts | `git ls-tree -r --name-only $R AitherOS/apps/AitherVeil/content/blog \| grep -c '\.md$'` | 301 |
| routines | `git ls-tree -r --name-only $R AitherOS/config/routines \| grep -c '\.yaml$'` | 222 |
| agents | `len(yaml.safe_load(config/agent-portraits.yaml)['agents'])` | 48 |
| aw* bricks | `yaml.safe_load(config/ecosystem.yaml)['bricks']` | 86 (public 55, no-pages 11, planned 13, unpublished 6, merged 1) |
| aw* stacks | same, `stacks` | 26 |
| org public repos | `gh repo list Aitherium --limit 300 --visibility public --json name -q length` | 87 |
| PyPI | `curl https://pypi.org/pypi/<pkg>/json` | awdk 3.8.60, awgit 1.12.0, awgraph 1.4.14, awrelay 0.5.0 |
| embedder | blog `code-search-embedder-13x-smaller-beats-its-teacher.md` | 13x smaller, beats teacher, $3 |

Changed meaning since 2026-09-20: "agents" was `ls .claude/agents` (33 then, 13 now — the session
roster was pruned); it is now the platform's public agent roster (agent-portraits.yaml), 48.
"Public bricks" fell 63 -> 55 because ecosystem.yaml split out a `no-pages` status (11).

USAF / Tanium / Boeing figures are from the owner's LinkedIn profile (2026-09-03 export) and were not re-measured here.
