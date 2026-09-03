"""Emit docs/index.html from docs/template.html + facts/*.

    python docs/build.py

Design system: the .ELEMENT base stylesheet and universe strip renderer are inlined
VERBATIM (facts/element/aitherium.css, facts/element/universe.js — vendored copies of
.ELEMENT/web/*; refresh them from the design-system tree, never hand-edit). Numbers
come from facts/resume.yaml + facts/bricks.json, the same files the resume and
video read, so the four artifacts cannot disagree.
"""
from __future__ import annotations

import io
import json
import re
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
TEMPLATE = HERE / "template.html"
OUT = HERE / "index.html"
ELEMENT = ROOT / "facts" / "element"

METRICS_TABLE = [  # key, label, how measured (from facts/measured.md)
    ("commits_total", "commits since 2025-06-08", "git rev-list --count HEAD"),
    ("commits_90d", "commits, last 90 days", "git rev-list --count --since='90 days ago' HEAD"),
    ("quality_gates", "self-testing quality gates", "git ls-files 'AitherOS/dev/tools/check_*.py' | wc -l"),
    ("mcp_tools_served", "MCP tools served", "gateway tools/list (1204-1211 on probe)"),
    ("compose_services", "services declared", "grep -cE '^  [a-z][a-z0-9-]+:$' docker-compose.aitheros.yml"),
    ("blog_posts", "posts written + published by agents", "ls AitherVeil/content/blog/*.md | wc -l"),
    ("aw_bricks_registered", "aw* bricks registered (40 public)", "yaml.safe_load(ecosystem.yaml)['bricks']"),
    ("routines", "scheduled routines", "ls AitherOS/config/routines/*.yaml | wc -l"),
    ("agents", "specialised agents", "ls .claude/agents | wc -l"),
    ("org_public_repos", "public repos, Aitherium org", "gh repo list Aitherium --json visibility"),
]


def main() -> int:
    facts = yaml.safe_load(io.open(ROOT / "facts" / "resume.yaml", encoding="utf-8"))
    eco = json.load(io.open(ROOT / "facts" / "bricks.json", encoding="utf-8"))
    css = (ELEMENT / "aitherium.css").read_text(encoding="utf-8")
    uni = (ELEMENT / "universe.js").read_text(encoding="utf-8")
    if "@element-tokens" not in css or "@element-universe" not in uni:
        raise SystemExit("facts/element/* is not the .ELEMENT web layer — refresh the vendored copies")
    m = facts["metrics"]
    payload = {
        "identity": facts["identity"],
        "summary": " ".join(facts["summary"].split()),
        "metrics": [{"key": k, "value": m[k], "label": lbl, "how": how} for k, lbl, how in METRICS_TABLE],
        "pypi": m["pypi"],
        "jd": [{"jd": r["jd"], "proof": " ".join(r["proof"].split())} for r in facts["jd_map"]],
        "experience": [
            {"org": e["org"], "title": e["title"], "dates": e["dates"], "bullets": e["bullets"]}
            for e in facts["experience"]
        ],
        "links": facts["links"],
        "bricks": eco["bricks"],
        "stacks": eco["stacks"],
    }
    data_js = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = TEMPLATE.read_text(encoding="utf-8")
    for tok, val in {
        "{{AITHERIUM_CSS}}": css,
        "{{UNIVERSE_JS}}": uni.replace("</script", "<\\/script"),
        "{{DATA_JSON}}": data_js,
        "{{COMMITS}}": f"{m['commits_total']:,}",
        "{{GATES}}": str(m["quality_gates"]),
        "{{BRICKS}}": str(m["aw_bricks_registered"]),
        "{{PUBLIC}}": str(m["aw_bricks_public"]),
    }.items():
        html = html.replace(tok, val)
    leftover = re.findall(r"\{\{[A-Z_]+\}\}", html)
    if leftover:
        raise SystemExit(f"unfilled tokens: {leftover}")
    OUT.write_text(html, encoding="utf-8", newline="\n")
    print(f"wrote {OUT} ({OUT.stat().st_size:,} bytes), bricks={len(eco['bricks'])}, stacks={len(eco['stacks'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
