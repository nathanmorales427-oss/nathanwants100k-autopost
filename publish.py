"""Post today's carousel (queue/<YYYY-MM-DD>, Quito date) to Instagram via the official Instagram API.

Runs in GitHub Actions. Needs the repo secret IG_TOKEN (Nathan pastes it himself; it is never in the repo).
Flow: one container per slide (is_carousel_item) -> one CAROUSEL container -> wait until FINISHED -> publish.
Images are fetched by Instagram from this public repo's raw URLs, so slides must be committed before this runs.
DRY_RUN=1 checks the folder, the caption and that every image URL is reachable, without posting.
"""
import datetime
import json
import os
import shutil
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://graph.instagram.com/v22.0"
HERE = Path(__file__).resolve().parent
TZ = datetime.timezone(datetime.timedelta(hours=-5))  # Quito (no daylight saving) = 6 PM post time anchor


def call(method, path, **params):
    params["access_token"] = os.environ["IG_TOKEN"]
    data = urllib.parse.urlencode(params).encode()
    url = f"{API}/{path}"
    if method == "GET":
        req = urllib.request.Request(url + "?" + data.decode())
    else:
        req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:  # show Instagram's error message, never the token
        sys.exit(f"Instagram API error on {path}: {e.code} {e.read().decode()[:500]}")


def reachable(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=30) as r:
            return r.status == 200
    except Exception:
        return False


def main():
    day = os.environ.get("POST_DATE") or datetime.datetime.now(TZ).strftime("%Y-%m-%d")
    folder = HERE / "queue" / day
    if not folder.exists():
        print(f"nothing queued for {day} (deleted = vetoed, or the queue ran dry)")
        return
    slides = sorted(folder.glob("slide_*.jpg"))
    caption = (folder / "caption.txt").read_text(encoding="utf-8").strip()
    if not 2 <= len(slides) <= 10:
        sys.exit(f"{day}: need 2-10 slides, found {len(slides)}")
    repo = os.environ.get("GITHUB_REPOSITORY", "nathanmorales427-oss/nathanwants100k-autopost")
    urls = [f"https://raw.githubusercontent.com/{repo}/main/queue/{day}/{s.name}" for s in slides]
    bad = [u for u in urls if not reachable(u)]
    if bad:
        sys.exit(f"images not reachable yet (pushed?): {bad}")
    print(f"{day}: {len(slides)} slides, caption {len(caption)} chars")
    if os.environ.get("DRY_RUN") == "1":
        print("DRY RUN: everything checks out, nothing posted")
        return
    me = call("GET", "me", fields="user_id,username")
    print("posting as @" + me.get("username", "?"))
    kids = [call("POST", "me/media", image_url=u, is_carousel_item="true")["id"] for u in urls]
    parent = call("POST", "me/media", media_type="CAROUSEL", children=",".join(kids), caption=caption)["id"]
    for _ in range(30):  # Instagram processes the container before it can be published
        st = call("GET", parent, fields="status_code").get("status_code")
        if st == "FINISHED":
            break
        if st == "ERROR":
            sys.exit("Instagram could not process the carousel (status ERROR)")
        time.sleep(5)
    media = call("POST", "me/media_publish", creation_id=parent)["id"]
    print(f"PUBLISHED media id {media}")
    (folder / "posted.json").write_text(json.dumps({"media_id": media, "posted_at": datetime.datetime.now(TZ)
                                                    .isoformat(timespec="seconds")}, indent=1), encoding="utf-8")
    dest = HERE / "posted" / day
    dest.parent.mkdir(exist_ok=True)
    shutil.move(str(folder), str(dest))


if __name__ == "__main__":
    main()
