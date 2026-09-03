"""Two-slide probe on the live renderer: proves the quote glyphs and the Inter headline
face before spending 11 minutes on the full deck. No narration, no music."""
import json, os, sys, time
os.chdir(r"C:\AitherOS-Fresh\AitherOS")
sys.path[:0] = [r"C:\AitherOS-Fresh\AitherOS", r"C:\AitherOS-Fresh\AitherOS\apps\awnode"]
os.environ.setdefault("AITHER_LIBRARY_ROOT", r"C:\AitherOS-Data\Library")
from tools.mcp import mcp_presentation as mp
mp._REMOTION_URL = "http://127.0.0.1:3700"
slides = [
    {"layout": "quote", "title": "Probe", "quote": "Scars from every layer.", "attribution": "David Parkhurst", "duration_seconds": 4},
    {"layout": "bullets", "title": "Architect multi-agent systems", "bullets": ["one", "two"], "duration_seconds": 4},
]
t0 = time.time()
out = mp.render_presentation_video(name="probe-fonts-0903", slides_json=json.dumps(slides), title="probe",
                                   theme="dark", accent_color="#2AD7D7", narrate=False, auto_pace=True, format="mp4")
print(f"ELAPSED {time.time()-t0:.0f}s"); print(out)
