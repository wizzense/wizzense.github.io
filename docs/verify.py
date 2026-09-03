import subprocess, sys, time, socket, pathlib
from playwright.sync_api import sync_playwright
site = pathlib.Path(__file__).resolve().parent
shots = site / "_shots"; shots.mkdir(exist_ok=True)
port = 8765
srv = subprocess.Popen([sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"], cwd=site, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    for _ in range(50):
        try: socket.create_connection(("127.0.0.1", port), timeout=0.2).close(); break
        except OSError: time.sleep(0.1)
    errors = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        for w, h, name in [(1366, 900, "desktop"), (390, 844, "mobile")]:
            pg = b.new_page(viewport={"width": w, "height": h})
            pg.on("console", lambda m: errors.append((m.type, m.text)) if m.type == "error" else None)
            pg.on("pageerror", lambda e: errors.append(("pageerror", str(e))))
            pg.goto(f"http://127.0.0.1:{port}/index.html", wait_until="networkidle")
            pg.wait_for_timeout(1500)
            bricks = pg.locator("li.brick").count()
            pg.screenshot(path=str(shots / f"{name}.png"), full_page=True)
            print(f"{name}: {w}x{h} bricks={bricks} shot={shots / (name + '.png')}")
            pg.close()
        b.close()
    print("console errors:", len(errors))
    for e in errors: print("  ", e)
finally:
    srv.terminate()
