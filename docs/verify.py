"""Serve docs/ locally, render it in Chromium at two viewports, drive the shell, and
assert zero console errors. Exit 1 on any error or missing element.

    python docs/verify.py
"""
import pathlib
import socket
import subprocess
import sys
import time

from playwright.sync_api import sync_playwright

site = pathlib.Path(__file__).resolve().parent
shots = site / "_shots"
shots.mkdir(exist_ok=True)
port = 8765
srv = subprocess.Popen(
    [sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"],
    cwd=site, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
)
rc = 0
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
        for w, h, name in [(1366, 900, "desktop"), (390, 844, "mobile")]:
            pg = b.new_page(viewport={"width": w, "height": h})
            pg.on("console", lambda m: errors.append((m.type, m.text)) if m.type == "error" else None)
            pg.on("pageerror", lambda e: errors.append(("pageerror", str(e))))
            pg.goto(f"http://127.0.0.1:{port}/index.html", wait_until="networkidle")
            pg.wait_for_timeout(1800)
            pg.screenshot(path=str(shots / f"{name}-boot.png"))
            pg.wait_for_selector("body.booted", timeout=15000)  # boot finishes on its own
            pg.wait_for_timeout(1300)
            pg.screenshot(path=str(shots / f"{name}-hero.png"))
            fonts = pg.evaluate("[...document.fonts].filter(f=>f.status==='loaded').map(f=>f.family).filter((v,i,a)=>a.indexOf(v)===i)")
            h1font = pg.evaluate("getComputedStyle(document.querySelector('#hero h1')).fontFamily")
            pg.locator("#shell").scroll_into_view_if_needed()
            pg.wait_for_timeout(300)
            pg.locator("#cmd").fill("stack")
            pg.locator("#cmd").press("Enter")
            pg.wait_for_timeout(900)
            bricks = pg.locator("#out .brick").count()
            pg.screenshot(path=str(shots / f"{name}-shell.png"))
            pg.locator("#cmd").fill("top")
            pg.locator("#cmd").press("Enter")
            pg.wait_for_timeout(1500)
            rows = pg.locator("#out .mrow").count()
            nodes = pg.locator("#constellation circle.node").count()
            for sec in ("stack", "factory"):
                pg.locator("#" + sec).scroll_into_view_if_needed()
                pg.wait_for_timeout(900)
                pg.screenshot(path=str(shots / f"{name}-{sec}.png"))
            pg.locator("#constellation").scroll_into_view_if_needed()
            pg.wait_for_timeout(900)
            pg.screenshot(path=str(shots / f"{name}-constellation.png"))
            pg.locator("#close").scroll_into_view_if_needed()
            pg.wait_for_timeout(900)
            pg.screenshot(path=str(shots / f"{name}-close.png"))
            print(f"{name}: {w}x{h} shell-bricks={bricks} metric-rows={rows} constellation-nodes={nodes}")
            print(f"  h1 font: {h1font} | loaded: {fonts}")
            if bricks != 64 or nodes != 64 or rows < 8:
                rc = 1
                print("  MISMATCH: expected 64 bricks / 64 nodes / >=8 metric rows")
            if "Cinzel" not in h1font:
                rc = 1
                print("  h1 is not Cinzel")
            pg.close()
        b.close()
    size = (site / "index.html").stat().st_size
    print(f"page weight: {size:,} bytes")
    if size > 400_000:
        rc = 1
        print("  page over 400 KB")
    print("console errors:", len(errors))
    for e in errors:
        print("  ", e)
    if errors:
        rc = 1
finally:
    srv.terminate()
sys.exit(rc)
