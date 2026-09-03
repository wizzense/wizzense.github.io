"""Host-side render: same tool the gateway serves, but Remotion reached over plain http
on the published loopback port (the registry entry lacks http_only, so in-fleet the URL
upgrades to https and Node answers WRONG_VERSION_NUMBER)."""
import json, os, sys, time
os.chdir(r"C:\AitherOS-Fresh\AitherOS")
sys.path[:0] = [r"C:\AitherOS-Fresh\AitherOS", r"C:\AitherOS-Fresh\AitherOS\apps\awnode"]
os.environ.setdefault("AITHER_LIBRARY_ROOT", r"C:\AitherOS-Data\Library")
from tools.mcp import mcp_presentation as mp
mp._REMOTION_URL = "http://127.0.0.1:3700"
# The tool pins the submit POST to 120 s; the rebuilt renderer loads Inter's full weight
# set per composition and an 11-slide submit now exceeds that (measured 2026-09-03: two
# "timed out" submits, the 2-slide probe passed). Widen the client for this run only.
_orig_csc = mp.create_sync_client
def _csc(timeout=120, **kw):
    return _orig_csc(timeout=max(timeout, 900), **kw)
mp.create_sync_client = _csc
slides = json.load(open(r"E:\repos\david-parkhurst\video\slides-public.json", encoding="utf-8"))
t0 = time.time()
out = mp.render_presentation_video(
    name="david-parkhurst-onebrief-public-cut",
    slides_json=json.dumps(slides),
    title="I built the factory that builds the software.",
    subtitle="wizzense - Outcome Engineer",
    author="wizzense",
    theme="dark", accent_color="#2AD7D7",
    background_music=r"C:\AitherOS-Fresh\.ELEMENTssets\musicisionary-tatami-main-version-25948-02-41.mp3", music_volume=0.06,
    narrate=True, voice="onyx", auto_pace=True, format="mp4",
)
print(f"ELAPSED {time.time()-t0:.0f}s")
print(out)
