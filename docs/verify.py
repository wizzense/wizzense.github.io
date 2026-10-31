"""Serve docs/ locally, render it in Chromium at two viewports, drive the living
desktop through one decision, and assert zero console errors. Exit 1 on any failure.

    python docs/verify.py
"""
import json
import pathlib
import socket
import subprocess
import sys
import time

from playwright.sync_api import sync_playwright

site = pathlib.Path(__file__).resolve().parent
shots = site / "_shots"
# expected counts come from the facts the page was built from, never a literal
WANT = sum(1 for b in json.loads((site.parent / "facts" / "bricks.json").read_text(encoding="utf-8"))["bricks"] if b.get("status") == "public")
shots.mkdir(exist_ok=True)
_s = socket.socket()
_s.bind(("127.0.0.1", 0))  # a free port: a fixed one collided with a peer's server
port = _s.getsockname()[1]
_s.close()
srv = subprocess.Popen(
    [sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"],
    cwd=site, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
)
rc = 0


def fail(msg):
    global rc
    rc = 1
    print("  FAIL:", msg)


try:
    for _ in range(50):
        try:
            socket.create_connection(("127.0.0.1", port), timeout=0.2).close()
            break
        except OSError:
            time.sleep(0.1)
    errors = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        for w, h, name, scheme in [(1366, 900, "desktop", "light"), (390, 844, "mobile", "dark")]:
            pg = b.new_page(viewport={"width": w, "height": h}, color_scheme=scheme)
            pg.on("console", lambda m: errors.append((m.type, m.text)) if m.type == "error" else None)
            pg.on("pageerror", lambda e: errors.append(("pageerror", str(e))))
            pg.on("requestfailed", lambda r: errors.append(("requestfailed", r.url)))
            pg.goto(f"http://127.0.0.1:{port}/index.html", wait_until="networkidle")
            pg.wait_for_timeout(600)
            pg.screenshot(path=str(shots / f"{name}-hero.png"))
            # the replay reaches the decision card on its own; approve it
            pg.locator("#desk").scroll_into_view_if_needed()
            pg.wait_for_selector("#w-code.on", timeout=15000)
            pg.wait_for_timeout(2500)
            pg.screenshot(path=str(shots / f"{name}-desk-work.png"))
            pg.wait_for_selector("#card.on", timeout=30000)
            pg.wait_for_timeout(500)
            pg.screenshot(path=str(shots / f"{name}-desk-card.png"))
            pg.locator("#approve").click()
            pg.wait_for_selector("#w-deploy.on", timeout=8000)
            pg.wait_for_selector("#w-film.on", timeout=15000)
            pg.wait_for_timeout(800)
            pg.screenshot(path=str(shots / f"{name}-desk-ship.png"))
            pg.screenshot(path=str(shots / f"{name}-full.png"), full_page=True)
            counts = pg.evaluate("""({rows:document.querySelectorAll('#rec .mrow').length,
              bricks:document.querySelectorAll('#bricklist .brick').length,
              cast:document.querySelectorAll('#castgrid figure').length,
              dock:document.querySelectorAll('#dock .a').length,
              log:document.querySelectorAll('#log li').length,
              xp:document.querySelectorAll('#xp .row').length,
              overflow:document.documentElement.scrollWidth - innerWidth,
              h1:getComputedStyle(document.querySelector('.hero h1')).fontFamily,
              broken:[...document.images].filter(i=>i.complete&&!i.naturalWidth).map(i=>i.src)})""")
            print(f"{name}: {w}x{h} {scheme} {counts}")
            if counts["rows"] < 8:
                fail("fewer than 8 record rows")
            if counts["bricks"] != WANT:
                fail(f"bricks {counts['bricks']} != public {WANT}")
            if counts["cast"] != 8 or counts["dock"] != 8:
                fail("cast/dock is not 8")
            if counts["log"] < 1 or counts["xp"] < 1:
                fail("recent log or experience empty")
            if counts["overflow"] > 0:
                fail(f"horizontal overflow {counts['overflow']}px")
            if "Instrument Serif" not in counts["h1"]:
                fail("h1 is not Instrument Serif")
            if counts["broken"]:
                fail(f"broken images {counts['broken']}")
            pg.close()
        b.close()
    size = (site / "index.html").stat().st_size
    print(f"page weight: {size:,} bytes")
    if size > 400_000:
        fail("page over 400 KB")
    print("console errors:", len(errors))
    for e in errors:
        print("  ", e)
    if errors:
        rc = 1
finally:
    srv.terminate()
sys.exit(rc)
