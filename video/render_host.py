"""Host-side render: same tool the gateway serves, but Remotion reached over plain http
on the published loopback port (the registry entry lacks http_only, so in-fleet the URL
upgrades to https and Node answers WRONG_VERSION_NUMBER)."""
import json, os, sys, time
os.chdir(r"C:\AitherOS-Fresh\AitherOS")
sys.path[:0] = [r"C:\AitherOS-Fresh\AitherOS", r"C:\AitherOS-Fresh\AitherOS\apps\awnode"]
os.environ.setdefault("AITHER_LIBRARY_ROOT", r"C:\AitherOS-Data\Library")
from tools.mcp import mcp_presentation as mp
mp._REMOTION_URL = "http://127.0.0.1:3700"
slides = json.load(open(r"E:\repos\david-parkhurst\video\slides.json", encoding="utf-8"))
t0 = time.time()
out = mp.render_presentation_video(
    name="david-parkhurst-onebrief-outcome-engineer-v2",
    slides_json=json.dumps(slides),
    title="I built the factory that builds the software.",
    subtitle="David Parkhurst - Outcome Engineer",
    author="David Parkhurst",
    theme="dark", accent_color="#2AD7D7",
    background_music=r"C:\AitherOS-Fresh\.ELEMENTssets\musicisionary-tatami-main-version-25948-02-41.mp3", music_volume=0.06,
    narrate=True, voice="onyx", auto_pace=True, format="mp4",
)
print(f"ELAPSED {time.time()-t0:.0f}s")
print(out)
