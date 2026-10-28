"""Manual mode helper (runs on Nathan's laptop): pull the queue from GitHub and mirror every upcoming carousel into
OneDrive\\Reels\\Ready\\Carousels\\<date> <show>\\ so it syncs to his phone, where he schedules it in the Instagram app.
Past dates are removed from that folder (they're posted). Safe to run any time; it only touches that one folder."""
import datetime
import json
import shutil
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent
DEST = Path(r"C:\Users\natha\OneDrive\Reels\Ready\Carousels")
TZ = datetime.timezone(datetime.timedelta(hours=-5))

subprocess.run(["git", "-C", str(REPO), "pull", "--ff-only", "-q"], check=False)
today = datetime.datetime.now(TZ).strftime("%Y-%m-%d")
DEST.mkdir(parents=True, exist_ok=True)
wanted = {}
for d in sorted((REPO / "queue").iterdir()):
    if d.is_dir() and d.name >= today and (d / "caption.txt").exists():
        show = json.loads((d / "post.json").read_text(encoding="utf-8")).get("show", "")
        wanted[f"{d.name} {show}".strip()] = d
for old in DEST.iterdir():  # gone from the queue or already past = posted
    if old.is_dir() and old.name not in wanted:
        shutil.rmtree(old)
for name, src in wanted.items():
    out = DEST / name
    out.mkdir(exist_ok=True)
    for f in list(src.glob("slide_*.jpg")) + [src / "caption.txt"]:
        shutil.copy2(f, out / f.name)
    if (src / "tiktok").exists():
        (out / "TikTok").mkdir(exist_ok=True)
        for f in (src / "tiktok").glob("slide_*.jpg"):
            shutil.copy2(f, out / "TikTok" / f.name)
print(f"{len(wanted)} upcoming carousel(s) in {DEST}")
