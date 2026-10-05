"""Emit docs/resume.pdf (the PUBLIC cut) from facts/resume.yaml.

    python docs/resume_build.py            # writes docs/resume.html + docs/resume.pdf

Same facts as the site and the film, so the three cannot disagree. Public identity only
(no full name, no city -- owner rule 2026-09-03). Brand: the Element tokens (true black,
one cyan) on paper, plus the personal mark -- the steel plate with the Ai Element mark.
Rendered by headless Chromium's print engine, US Letter, two pages.
"""
from __future__ import annotations

import html
import io
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
E = html.escape

CSS = """
@page { size: Letter; margin: 0.45in 0.5in; }
* { box-sizing: border-box; }
body { font-family: Inter, 'Segoe UI', Arial, sans-serif; color: #12161c; font-size: 9.0pt; line-height: 1.32; margin: 0; }
header { display: flex; align-items: center; gap: 16px; border-bottom: 2px solid #0e7f86; padding-bottom: 8px; margin-bottom: 8px; }
.plate { width: 78px; height: 36px; border-radius: 6px; flex: none; display: grid; place-items: center;
  background: linear-gradient(170deg,#eef2f6 0%,#b3bcc7 40%,#dfe5eb 60%,#99a4b1 100%); box-shadow: inset 0 -1px 2px rgba(0,0,0,.3); }
.plate img { width: 30px; height: 30px; filter: grayscale(1) contrast(1.4) brightness(.5); }
h1 { font-family: Cinzel, Georgia, serif; font-size: 20pt; letter-spacing: .04em; margin: 0; line-height: 1.05; }
h1 b { color: #0e7f86; font-weight: 700; }
.head { color: #3a4450; font-size: 9.8pt; margin-top: 2px; }
.persona { font-size: 8.8pt; color: #4b5563; font-style: italic; margin-top: 2px; }
.contact { margin-left: auto; text-align: right; font-size: 8.4pt; color: #3a4450; line-height: 1.5; }
h2 { font-size: 8.6pt; letter-spacing: .18em; text-transform: uppercase; color: #0e7f86; margin: 8px 0 3px; border-bottom: 1px solid #d5dbe1; padding-bottom: 2px; }
.summary { margin: 0; }
.metrics { display: grid; grid-template-columns: repeat(6, 1fr); gap: 4px; margin: 6px 0 2px; }
.m { border: 1px solid #d5dbe1; border-radius: 4px; padding: 3px 5px; }
.m b { display: block; font-size: 11.5pt; color: #0b1830; }
.m span { font-size: 7pt; color: #5b6572; text-transform: uppercase; letter-spacing: .06em; }
.recent { display: grid; grid-template-columns: 1fr 1fr; gap: 3px 14px; }
.recent div b { color: #0b1830; }
.job { margin-top: 6px; }
.job .t, .job li { break-inside: avoid; }
.job .t { display: flex; justify-content: space-between; font-weight: 600; }
.job .t span { font-weight: 400; color: #5b6572; }
.job ul { margin: 2px 0 0 14px; padding: 0; }
.job li { margin: 1px 0; }
.skills div { margin: 1px 0; }
.skills b { color: #0b1830; }
.foot { margin-top: 8px; font-size: 7.6pt; color: #6b7480; }
a { color: #0e7f86; text-decoration: none; }
"""


def build() -> str:
    f = yaml.safe_load(io.open(ROOT / "facts" / "resume.yaml", encoding="utf-8"))
    me, m = f["public_identity"], f["metrics"]
    tiles = [(f"{m['commits_total']:,}", "commits"), (f"{m['merged_prs_total']:,}", "merged PRs"),
             (f"{m['quality_gates']:,}", "self-testing gates"), (f"{m['mcp_tools_served']:,}", "MCP tools live"),
             (str(m["agents"]), "agents"), (str(m["blog_posts"]), "posts published")]
    mark = (HERE / "assets" / "element-symbol.svg").as_uri()
    out = [f"<!doctype html><html><head><meta charset='utf-8'><title>{E(me['name'])} - resume</title><style>{CSS}</style></head><body>"]
    out.append(f"<header><div class='plate'><img src='{mark}' alt=''></div><div>"
               f"<h1>David <b>wizzense</b></h1><div class='head'>{E(me['headline'])}</div>"
               f"<div class='persona'>The copy ninja: see a technique once, and the factory performs it a thousand times.</div></div>"
               f"<div class='contact'>{E(me['email'])}<br>{E(me['site'])}<br>{E(me['github'])} · {E(me['org'])}<br>{E(me['blog'])}</div></header>")
    summary = " ".join(f["summary"].split()).replace("Onebrief's Outcome Engineering charter", "Platform engineering")
    out.append("<h2>Summary</h2><p class='summary'>" + E(summary) + "</p>")
    out.append("<div class='metrics'>" + "".join(f"<div class='m'><b>{v}</b><span>{E(k)}</span></div>" for v, k in tiles) + "</div>")
    out.append(f"<h2>Since September 20 &middot; {m['merged_prs_since_2026_09_20']:,} merged PRs, {m['feature_prs_since_2026_09_20']} features</h2><div class='recent'>")
    out += [f"<div><b>{E(r['title'])}.</b> {E(r['body'])}</div>" for r in f.get("recent", [])]
    out.append("</div><h2>Experience</h2>")
    for e in f["experience"]:
        out.append(f"<div class='job'><div class='t'>{E(e['org'])} &mdash; {E(e['title'])}<span>{E(e['dates'])}</span></div><ul>"
                   + "".join(f"<li>{E(b)}</li>" for b in e["bullets"]) + "</ul></div>")
    out.append("<h2>Skills</h2><div class='skills'>" + "".join(
        f"<div><b>{E(k)}:</b> {E(', '.join(v))}</div>" for k, v in f["skills"].items()) + "</div>")
    out.append("<h2>Certifications</h2><div>" + E(" · ".join(f["certs"])) + "</div>")
    out.append("<div class='foot'>Every number above was measured on the AitherOS tree; the command behind each is in "
               "github.com/wizzense/wizzense.github.io/facts/measured.md.</div></body></html>")
    return "".join(out)


def main() -> int:
    from playwright.sync_api import sync_playwright
    page_html = HERE / "resume.html"
    page_html.write_text(build(), encoding="utf-8")
    pdf = HERE / "resume.pdf"
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        pg.goto(page_html.as_uri())
        pg.wait_for_timeout(600)
        pg.pdf(path=str(pdf), format="Letter", print_background=True,
               margin={"top": "0.4in", "bottom": "0.4in", "left": "0.45in", "right": "0.45in"})
        b.close()
    print(f"wrote {pdf} ({pdf.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
