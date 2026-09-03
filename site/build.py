"""Generate site/index.html from facts/resume.yaml + facts/bricks.json.

No build step is needed to SERVE the site; this script exists so the numbers on
the page come from the facts file rather than being typed twice.
"""
from __future__ import annotations

import html
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
FACTS = yaml.safe_load((ROOT / "facts" / "resume.yaml").read_text(encoding="utf-8"))
BRICKS = json.loads((ROOT / "facts" / "bricks.json").read_text(encoding="utf-8"))
M = FACTS["metrics"]
ID = FACTS["identity"]

E = html.escape

NUMBERS = [
    ("21065", "commits", "since 2025-06-08",
     "git rev-list --count HEAD on the AitherOS tree, 2026-09-03."),
    ("13928", "commits, last 90 days", "agent-authored under gates",
     "git rev-list --count --since='90 days ago' HEAD."),
    ("642", "self-testing quality gates", "each must prove it can fail",
     "git ls-files 'AitherOS/dev/tools/check_*.py' | wc -l. Every gate carries --self-test and is claimed by one of four unattended lanes."),
    ("1200", "MCP tools served", "263 tool modules, one gateway",
     "Gateway tools/list on probe (1204-1211 recorded); ls apps/awnode/tools/mcp/mcp_*.py = 263."),
    ("369", "services declared", "podman quadlets, 12 layers",
     "grep -cE '^  [a-z][a-z0-9-]+:$' .DEPLOYMENT/compose/docker-compose.aitheros.yml."),
    ("270", "blog posts published", "written and gated by agents",
     "ls apps/AitherVeil/content/blog/*.md | wc -l; served at blog.aitherium.com."),
    ("64", "aw* bricks registered", "40 public, 14 stacks",
     "AitherOS/config/ecosystem.yaml bricks[] (public 40, unpublished 15, planned 7, merged 1, no-pages 1); stacks[] = 14."),
    ("850000", "users on the AD I ran", "USAF, 690 DCs, 230 sites",
     "USAF Cyber Systems Operations, 2015-2020; second-largest Active Directory in the world. From service record / LinkedIn, not re-measured."),
]

TIMELINE = [
    ("2014 - 2020", "United States Air Force", "Cyber Systems Operations",
     "Ran Tier-2 for the second-largest Active Directory on earth: $10B, 850,000 users, 690 domain controllers, 230 sites, classified and unclassified, 24/7. Automated 70+ DCs in PowerShell. Authoritative ADDS restore of 3,000 accounts with zero collateral. Wrote the curriculum and trained 357 technicians. Red Flag 17-1 blue-team Superior Performer."),
    ("2020 - 2022", "Boeing", "HPC Linux System Engineer",
     "Owned the enterprise tape archive (Oracle HSM to Versity as technical lead) and a fibre-channel SAN under HPC load. Python automation for recovery, monitoring, archival. LTO6 to LTO8 migration; data-at-rest encryption with OKM 3 and IBM SKLM."),
    ("2022 - present", "Tanium", "Senior Enterprise Services Engineer / Escalation Engineer",
     "The hardest endpoint-management escalations for enterprise and federal customers. 195 cases in six months at 100% CSAT. Rewrote the Risk Assessment tooling to scale from 500 to unbounded endpoints; ran it on 50,000. Client Health dashboards and the webinar that went with them. 2x Star Performer."),
    ("2025 - present", "Aitherium", "Founder, Architect",
     "Built AitherOS and the aw* stack. 33 agents that plan, code, review, audit, deploy and write about their own work, behind 642 gates I designed. Three tenant appliances live with real customers. Four packages on PyPI, 61 public repos."),
]

DOCTRINE = [(m["jd"], m["proof"].strip()) for m in FACTS["jd_map"]]
DOCTRINE_TITLES = ["Orchestrate", "Govern", "Remember", "Evaluate", "Self-heal", "Ship"]

PROOF = FACTS["links"]


def brick_cards() -> str:
    out = []
    for b in BRICKS:
        st = b["status"] or "unknown"
        dim = "" if st == "public" else " brick--dim"
        chip = "" if st == "public" else f'<span class="chip">{E(st)}</span>'
        hero = " brick--hero" if b["id"] == "awnix" else ""
        out.append(
            f'<li class="brick{dim}{hero}"><span class="brick__id">{E(b["id"])}</span>'
            f'{chip}<p class="brick__tag">{E(b["tagline"]) or "&nbsp;"}</p></li>'
        )
    return "\n".join(out)


def numbers() -> str:
    out = []
    for raw, label, sub, how in NUMBERS:
        display = raw
        prefix = "~" if raw == "1200" else ""
        out.append(
            f'<li class="num"><span class="num__v" data-count="{raw}">{prefix}{int(raw):,}</span>'
            f'<span class="num__l">{E(label)}</span><span class="num__s">{E(sub)}</span>'
            f'<details class="num__how"><summary>how measured</summary><p>{E(how)}</p></details></li>'
        )
    return "\n".join(out)


def timeline() -> str:
    return "\n".join(
        f'<li class="tl"><span class="tl__when">{E(w)}</span><h3 class="tl__org">{E(o)}</h3>'
        f'<p class="tl__role">{E(r)}</p><p class="tl__body">{E(b)}</p></li>'
        for w, o, r, b in TIMELINE
    )


def doctrine() -> str:
    return "\n".join(
        f'<li class="doc"><h3 class="doc__t"><span class="doc__n">{i+1:02d}</span> {E(t)}</h3>'
        f'<p class="doc__jd">{E(jd)}</p><p class="doc__p">{E(p)}</p></li>'
        for i, ((jd, p), t) in enumerate(zip(DOCTRINE, DOCTRINE_TITLES))
    )


def proof() -> str:
    items = [(l["label"], l["url"]) for l in PROOF if "this site" not in l["label"]]
    items.append(("Resume (PDF)", "resume.pdf"))
    items.append(("PyPI: awdk " + M["pypi"]["awdk"] + ", awgit " + M["pypi"]["awgit"]
                  + ", awgraph " + M["pypi"]["awgraph"] + ", awrelay " + M["pypi"]["awrelay"],
                  "https://pypi.org/user/wizzense/"))
    return "\n".join(
        f'<li><a class="proof" href="{E(u)}" {"target=_blank rel=noopener" if u.startswith("http") else ""}>'
        f'<span>{E(l)}</span><span class="proof__u">{E(u.replace("https://", ""))}</span></a></li>'
        for l, u in items
    )


PAGE = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>David Parkhurst — Outcome Engineer</title>
<meta name="description" content="David Parkhurst. Outcome Engineer. Founder and architect of AitherOS, awnix and the aw* stack. USAF veteran. I built the factory that builds the software.">
<meta property="og:title" content="David Parkhurst — Outcome Engineer">
<meta property="og:description" content="I built the factory that builds the software. 21,065 commits, 642 self-testing gates, 1,200 MCP tools, 64 aw* bricks.">
<meta name="color-scheme" content="dark">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=JetBrains+Mono:wght@400;600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root{{
  --bg:#0a0a0f; --bg2:#101018; --bg3:#161623; --line:#23233a;
  --fg:#e8e8f0; --mute:#8f8fa8; --dim:#5c5c74;
  --acc:#7c5cff; --acc2:#b9a6ff; --acc-dim:rgba(124,92,255,.14);
  --serif:"Instrument Serif",Georgia,"Times New Roman",serif;
  --sans:Inter,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
  --mono:"JetBrains Mono",ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  --max:1120px;
}}
*{{box-sizing:border-box}}
html{{scroll-behavior:smooth}}
body{{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 var(--sans);-webkit-font-smoothing:antialiased}}
a{{color:var(--acc2);text-decoration:none}}
a:hover{{text-decoration:underline;text-decoration-thickness:1px;text-underline-offset:3px}}
h1,h2,h3{{font-weight:400;margin:0}}
.wrap{{max-width:var(--max);margin:0 auto;padding:0 24px}}
section{{padding:88px 0;border-top:1px solid var(--line)}}
.kicker{{font:600 12px/1 var(--mono);letter-spacing:.14em;text-transform:uppercase;color:var(--acc);margin-bottom:18px}}
.kicker::before{{content:"// ";color:var(--dim)}}
h2{{font:400 clamp(30px,4.4vw,48px)/1.1 var(--serif);letter-spacing:-.01em;margin-bottom:40px}}
h2 em{{font-style:italic;color:var(--acc2)}}
/* hero */
.hero{{padding:120px 0 96px;position:relative;overflow:hidden;border-top:0}}
.hero::before{{content:"";position:absolute;inset:-40% -20% auto -20%;height:120%;background:radial-gradient(ellipse at 30% 0%,var(--acc-dim),transparent 55%);pointer-events:none}}
.hero .prompt{{font:14px var(--mono);color:var(--dim);margin-bottom:22px}}
.hero .prompt b{{color:var(--acc);font-weight:600}}
.hero h1{{font:400 clamp(48px,9vw,112px)/.98 var(--serif);letter-spacing:-.025em}}
.hero h1 span{{display:block;color:var(--mute)}}
.hero .line{{font:400 clamp(20px,2.6vw,30px)/1.3 var(--serif);color:var(--fg);margin:34px 0 14px;max-width:760px}}
.hero .line em{{color:var(--acc2)}}
.hero .sub{{color:var(--mute);max-width:640px;margin:0 0 36px}}
.links{{display:flex;flex-wrap:wrap;gap:12px;list-style:none;padding:0;margin:0}}
.links a{{font:500 14px var(--mono);border:1px solid var(--line);padding:10px 16px;border-radius:6px;color:var(--fg);background:var(--bg2);transition:border-color .2s,transform .2s}}
.links a:hover{{border-color:var(--acc);text-decoration:none;transform:translateY(-1px)}}
.links a::before{{content:"→ ";color:var(--acc)}}
/* numbers */
.nums{{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:var(--line);border:1px solid var(--line);border-radius:10px;overflow:hidden}}
.num{{background:var(--bg2);padding:26px 22px 18px;display:flex;flex-direction:column;gap:4px;min-height:170px}}
.num__v{{font:600 clamp(30px,3.6vw,44px)/1 var(--mono);color:var(--fg);letter-spacing:-.03em;font-variant-numeric:tabular-nums}}
.num__l{{font:500 14px var(--sans);color:var(--fg);margin-top:8px}}
.num__s{{font:13px var(--sans);color:var(--mute)}}
.num__how{{margin-top:auto;padding-top:10px;font:12px var(--mono);color:var(--dim)}}
.num__how summary{{cursor:pointer;list-style:none;color:var(--dim)}}
.num__how summary::before{{content:"? ";color:var(--acc)}}
.num__how summary::-webkit-details-marker{{display:none}}
.num__how p{{margin:8px 0 0;color:var(--mute);line-height:1.5;font-family:var(--sans);font-size:12.5px}}
.measured-note{{font:13px var(--mono);color:var(--dim);margin-top:16px}}
/* timeline */
.tls{{list-style:none;padding:0;margin:0;display:grid;gap:0;border-left:1px solid var(--line);margin-left:6px}}
.tl{{position:relative;padding:0 0 44px 36px}}
.tl::before{{content:"";position:absolute;left:-6px;top:8px;width:11px;height:11px;border-radius:50%;background:var(--bg);border:2px solid var(--acc)}}
.tl:last-child::before{{background:var(--acc)}}
.tl__when{{font:600 12px var(--mono);letter-spacing:.1em;color:var(--acc);text-transform:uppercase}}
.tl__org{{font:400 30px/1.15 var(--serif);margin:6px 0 2px}}
.tl__role{{margin:0 0 10px;color:var(--mute);font-size:14px}}
.tl__body{{margin:0;max-width:760px;color:#c9c9d8}}
.stack-quote{{font:400 clamp(22px,3vw,34px)/1.3 var(--serif);max-width:820px;margin:0 0 56px;color:var(--fg)}}
.stack-quote em{{color:var(--acc2)}}
/* built */
.built-lead{{max-width:760px;color:#c9c9d8;margin:0 0 40px}}
.built-lead strong{{color:var(--fg);font-weight:600}}
.bricks{{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:10px}}
.brick{{background:var(--bg2);border:1px solid var(--line);border-radius:8px;padding:14px 14px 12px;display:flex;flex-direction:column;gap:6px;transition:border-color .2s}}
.brick:hover{{border-color:var(--acc)}}
.brick__id{{font:600 14px var(--mono);color:var(--acc2)}}
.brick__tag{{margin:0;font-size:13px;line-height:1.45;color:#c9c9d8}}
.brick--dim{{opacity:.55}}
.brick--dim .brick__id{{color:var(--mute)}}
.brick--hero{{grid-column:1/-1;background:linear-gradient(135deg,var(--acc-dim),var(--bg2) 60%);border-color:var(--acc);padding:24px}}
.brick--hero .brick__id{{font-size:28px;color:var(--fg)}}
.brick--hero .brick__id::after{{content:"  — the one I'd hand you first";font-size:14px;color:var(--acc2);font-weight:400}}
.brick--hero .brick__tag{{font-size:17px;max-width:720px}}
.chip{{align-self:flex-start;font:600 10px var(--mono);letter-spacing:.1em;text-transform:uppercase;color:var(--mute);border:1px solid var(--line);border-radius:4px;padding:2px 6px}}
.bricks-note{{font:13px var(--mono);color:var(--dim);margin-top:18px}}
/* doctrine */
.docs{{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(3,1fr);gap:14px}}
.doc{{background:var(--bg2);border:1px solid var(--line);border-radius:10px;padding:24px;display:flex;flex-direction:column;gap:8px}}
.doc__t{{font:400 28px/1.1 var(--serif)}}
.doc__n{{font:600 13px var(--mono);color:var(--acc);margin-right:6px;vertical-align:middle}}
.doc__jd{{margin:0;font:600 11px var(--mono);letter-spacing:.1em;text-transform:uppercase;color:var(--mute)}}
.doc__p{{margin:6px 0 0;font-size:14px;line-height:1.6;color:#c9c9d8}}
/* proof */
.proofs{{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(2,1fr);gap:10px}}
.proof{{display:flex;flex-direction:column;gap:3px;background:var(--bg2);border:1px solid var(--line);border-radius:8px;padding:16px 18px;color:var(--fg);transition:border-color .2s}}
.proof:hover{{border-color:var(--acc);text-decoration:none}}
.proof__u{{font:12px var(--mono);color:var(--dim);word-break:break-all}}
/* footer */
footer{{border-top:1px solid var(--line);padding:56px 0 72px;color:var(--mute);font-size:14px}}
footer .sig{{font:400 26px var(--serif);color:var(--fg);margin-bottom:8px}}
footer a{{font-family:var(--mono)}}
footer .fine{{font:12px var(--mono);color:var(--dim);margin-top:24px}}
@media (max-width:900px){{.nums{{grid-template-columns:repeat(2,1fr)}}.docs{{grid-template-columns:1fr 1fr}}}}
@media (max-width:600px){{section{{padding:64px 0}}.hero{{padding:80px 0 64px}}.nums,.docs,.proofs{{grid-template-columns:1fr}}.num{{min-height:0}}.tl{{padding-left:26px}}}}
@media (prefers-reduced-motion:reduce){{*{{transition:none!important;animation:none!important}}html{{scroll-behavior:auto}}}}
</style>
</head>
<body>
<main>
<header class="hero">
  <div class="wrap">
    <p class="prompt"><b>aither@wizzense</b> ~ $ whoami</p>
    <h1>David<span>Parkhurst.</span></h1>
    <p class="line">Outcome Engineer. <em>I built the factory that builds the software.</em></p>
    <p class="sub">Founder and architect of AitherOS, awnix and the aw* stack. USAF veteran who ran an 850,000-user directory before most people had heard of an agent. Every number on this page has the command that produced it.</p>
    <ul class="links">
      <li><a href="https://github.com/wizzense" target="_blank" rel="noopener">github.com/wizzense</a></li>
      <li><a href="https://www.linkedin.com/in/david-a-parkhurst" target="_blank" rel="noopener">linkedin.com/in/david-a-parkhurst</a></li>
      <li><a href="https://blog.aitherium.com" target="_blank" rel="noopener">blog.aitherium.com</a></li>
    </ul>
  </div>
</header>

<section id="measured" aria-labelledby="h-measured">
  <div class="wrap">
    <p class="kicker">measured</p>
    <h2 id="h-measured">Not claimed. <em>Measured.</em></h2>
    <ul class="nums">
{numbers()}
    </ul>
    <p class="measured-note">All figures measured 2026-09-03 on the AitherOS tree. A number without its command is an opinion; open "how measured" on any card.</p>
  </div>
</section>

<section id="stack" aria-labelledby="h-stack">
  <div class="wrap">
    <p class="kicker">the full stack, every layer</p>
    <h2 id="h-stack">Not many people can say they own and control the full stack. <em>I can.</em></h2>
    <p class="stack-quote">I've racked the servers, managed the SAN, administered the OS at 850K-user scale, secured the network, automated the operations, built the APIs, designed the data pipelines, trained the models, scheduled the GPUs, written the Terraform, and built the React dashboard that sits on top of all of it. <em>I don't have gaps in the stack. I have scars from every layer.</em></p>
    <ol class="tls">
{timeline()}
    </ol>
  </div>
</section>

<section id="built" aria-labelledby="h-built">
  <div class="wrap">
    <p class="kicker">what i built</p>
    <h2 id="h-built">AitherOS, and the <em>aw* stack</em> underneath it.</h2>
    <p class="built-lead"><strong>AitherOS</strong> is an AI-native operating platform: {M["compose_services"]} declared services across 12 layers, {M["agents"]} specialised agents behind one MCP gateway serving {M["mcp_tools_served"]} tools, a priority scheduler that owns every LLM call across a local RTX 5090, a DGX Spark pool and rented cloud GPUs, and {M["quality_gates"]} gates that decide what ships. The agents plan, code, review, audit, deploy and write about their own work; the gates make sure they are telling the truth.</p>
    <p class="built-lead"><strong>aw*</strong> is short for <em>Aither World</em>. Each brick is one thing a stranger can adopt alone; stacks compose them. {M["aw_bricks_registered"]} registered, {M["aw_bricks_public"]} public, {M["aw_stacks"]} stacks, four on PyPI. A brick is not shipped when it builds; it is shipped when it is reachable from where people look, and a gate enforces that.</p>
    <ul class="bricks">
{brick_cards()}
    </ul>
    <p class="bricks-note">{len(BRICKS)} bricks rendered from AitherOS/config/ecosystem.yaml. Dimmed = registered, not yet public. An absence with a name can be chased; a silent one gets rediscovered.</p>
  </div>
</section>

<section id="how" aria-labelledby="h-how">
  <div class="wrap">
    <p class="kicker">how i work</p>
    <h2 id="h-how">Six things an autonomous factory must do, <em>and what I built for each.</em></h2>
    <ol class="docs">
{doctrine()}
    </ol>
  </div>
</section>

<section id="proof" aria-labelledby="h-proof">
  <div class="wrap">
    <p class="kicker">proof</p>
    <h2 id="h-proof">Go look. <em>It's all public.</em></h2>
    <ul class="proofs">
{proof()}
    </ul>
  </div>
</section>
</main>

<footer>
  <div class="wrap">
    <p class="sig">David Parkhurst</p>
    <p><a href="mailto:{E(ID["email"])}">{E(ID["email"])}</a> · {E(ID["location"])}</p>
    <p class="fine">This page has no build step, no framework and no tracker. The numbers were measured by the same gates that gate the code. Last measured 2026-09-03.</p>
  </div>
</footer>

<script>
(function(){{
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var els = document.querySelectorAll('.num__v[data-count]');
  if (reduce || !('IntersectionObserver' in window)) return;
  var fmt = function(n){{ return n.toLocaleString('en-US'); }};
  var run = function(el){{
    var target = parseInt(el.getAttribute('data-count'), 10);
    var prefix = el.textContent.charAt(0) === '~' ? '~' : '';
    var t0 = null, dur = 1100;
    var step = function(ts){{
      if (!t0) t0 = ts;
      var p = Math.min(1, (ts - t0) / dur);
      var e = 1 - Math.pow(1 - p, 3);
      el.textContent = prefix + fmt(Math.round(target * e));
      if (p < 1) requestAnimationFrame(step); else el.textContent = prefix + fmt(target);
    }};
    requestAnimationFrame(step);
  }};
  var io = new IntersectionObserver(function(entries){{
    entries.forEach(function(en){{
      if (en.isIntersecting) {{ run(en.target); io.unobserve(en.target); }}
    }});
  }}, {{threshold: 0.4}});
  els.forEach(function(el){{ io.observe(el); }});
}})();
</script>
</body>
</html>
"""

(ROOT / "site" / "index.html").write_text(PAGE, encoding="utf-8")
(ROOT / "site" / ".nojekyll").write_text("", encoding="utf-8")
print("wrote index.html", len(PAGE), "bytes;", len(BRICKS), "bricks")
