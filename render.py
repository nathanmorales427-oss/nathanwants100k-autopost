"""Render one carousel from queue/<date>/post.json into "post in a post" slides (Pillow only, runs in the cloud).

post.json:
{
  "show": "Money History",
  "slides": [{"text": "...", "photo": "photos/a.jpg", "credit": "Photo: ... / CC BY-SA 4.0", "focus": [0.5, 0.3],
              "photo_h": 470, "gray": true}, ...],      # 2-10 slides; photo optional
  "caption": "...",
  "sources": ["https://...", ...]                        # every number on the slides must trace to one of these
}
Writes slide_01.jpg... (1080x1350 JPEG, what Instagram's API accepts) and tiktok/slide_01.jpg... (1080x1920).
Usage: python render.py queue/2026-10-29
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

HERE = Path(__file__).resolve().parent
FONT = HERE / "fonts" / "Inter.ttf"
PFP = HERE / "brand" / "pfp.jpg"
W, H, PAD = 1080, 1350, 70
NAME, HANDLE = "Nathan", "@nathanwants100k"
INK, GRAYTXT, LINE = (15, 20, 25), (83, 100, 113), (207, 217, 222)


def font(px, weight=400):
    f = ImageFont.truetype(str(FONT), px)
    f.set_variation_by_axes([min(32, max(14, px)), weight])
    return f


def wrap(text, f, width):
    """Paragraph-aware word wrap by pixel width. Returns a list of lines ('' = blank line)."""
    lines = []
    for para in text.split("\n"):
        if not para.strip():
            lines.append("")
            continue
        cur = ""
        for word in para.split(" "):
            test = (cur + " " + word).strip()
            if f.getlength(test) <= width:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def avatar(px):
    im = ImageOps.fit(Image.open(PFP).convert("RGB"), (px * 4, px * 4))
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).ellipse([0, 0, im.width - 1, im.height - 1], fill=255)
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.paste(im, (0, 0), m)
    return out.resize((px, px), Image.LANCZOS)


def rounded_photo(path, w, h, focus, gray):
    im = Image.open(path)
    im = ImageOps.exif_transpose(im).convert("RGB")
    im = ImageOps.fit(im, (w, h), Image.LANCZOS, centering=tuple(focus))
    if gray:
        im = ImageOps.grayscale(im).convert("RGB")
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], 30, fill=255)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.paste(im, (0, 0), m)
    ImageDraw.Draw(out).rounded_rectangle([0, 0, w - 1, h - 1], 30, outline=LINE, width=2)
    return out


def slide(s, folder):
    has_photo = bool(s.get("photo"))
    size = 46 if has_photo else 56
    f_txt = font(size, 400)
    lines = wrap(s["text"], f_txt, W - 2 * PAD)
    lh = int(size * 1.38)
    text_h = lh * len(lines)
    ph = None
    if has_photo:
        ph = rounded_photo(folder / s["photo"], W - 2 * PAD, s.get("photo_h", 470), s.get("focus", [0.5, 0.5]),
                           s.get("gray", False))
    av = 118
    block = av + 34 + text_h + ((34 + ph.height + (40 if s.get("credit") else 0)) if ph else 0)
    if block > H - 80:
        raise ValueError(f"slide too tall ({block}px): shorten the text or the photo")
    y = (H - block) // 2
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    img.paste(avatar(av), (PAD, y), avatar(av))
    d.text((PAD + av + 26, y + 18), NAME, font=font(42, 700), fill=INK)
    d.text((PAD + av + 26, y + 66), HANDLE, font=font(36, 400), fill=GRAYTXT)
    y += av + 34
    for ln in lines:
        d.text((PAD, y), ln, font=f_txt, fill=INK)
        y += lh
    if ph:
        y += 34
        img.paste(ph, (PAD, y), ph)
        y += ph.height
        if s.get("credit"):
            d.text((PAD, y + 10), s["credit"], font=font(20, 400), fill=(139, 152, 165))
    return img


def render(folder):
    folder = Path(folder)
    post = json.loads((folder / "post.json").read_text(encoding="utf-8"))
    slides = post["slides"]
    if not 2 <= len(slides) <= 10:
        raise ValueError("a carousel needs 2-10 slides (Instagram API limit)")
    if not post.get("sources"):
        raise ValueError("post.json needs its sources: every number must trace to one")
    (folder / "tiktok").mkdir(exist_ok=True)
    for i, s in enumerate(slides, 1):
        im = slide(s, folder)
        im.save(folder / f"slide_{i:02d}.jpg", quality=92)
        tall = Image.new("RGB", (1080, 1920), "white")
        tall.paste(im, (0, (1920 - H) // 2))
        tall.save(folder / "tiktok" / f"slide_{i:02d}.jpg", quality=92)
    (folder / "caption.txt").write_text(post["caption"].strip() + "\n", encoding="utf-8")
    print(f"rendered {len(slides)} slides -> {folder}")


if __name__ == "__main__":
    for f in sys.argv[1:]:
        render(f)
