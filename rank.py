"""Format "rank" (ab 17.11.): Blind Ranking. 5 Dinge kommen einzeln, der Zuschauer muss sie
sofort auf Platz 1-5 einordnen, ohne die naechsten zu kennen ("no changing your answer").
Klassischer Kommentar-Treiber: jeder hat eine Meinung, jeder postet seine Reihenfolge.

Aufruf:  python rank.py <set-id> [ausgabe.mp4]
"""
import json
import os
import sys

from PIL import Image

import reelkit as k
import render as r

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data", "ranks.json")
ACCENT = (255, 92, 160)
TOP, BOTTOM = (36, 8, 30), (10, 2, 10)
CARD = (70, 20, 56)
ROW_BG = (48, 14, 40)
CAPTIONS = [
    "Blind rank them 1 to 5. No changing your answer! Comment your ranking and send this to a friend to compare.",
    "You can't move anyone once placed. What's your 1-5? Comment it, then send this to a friend.",
    "Blind ranking: rank each one before you see the next. Drop your order in the comments and send it to your group.",
]


def load_sets():
    with open(DATA, encoding="utf-8") as f:
        return json.load(f)


def header(rset):
    img = k.gradient(TOP, BOTTOM)
    d = k.draw(img)
    width = r.SAFE_RIGHT - r.SAFE_LEFT
    d.text((r.SAFE_LEFT, 236), "BLIND RANK", font=r.fit_font(d, "BLIND RANK", r.BOLD, 120, width), fill=ACCENT)
    d.text((r.SAFE_LEFT, 372), rset["topic"], font=r.fit_font(d, rset["topic"], r.BOLD, 70, width), fill=r.WHITE)
    d.text((r.SAFE_LEFT, 462), "no changing your answer", font=r.font(r.REGULAR, 44), fill=(200, 160, 190))
    k.pill(d, 1507, rset.get("share", "SEND THIS TO A FRIEND AND COMPARE"), ACCENT, BOTTOM, 48)
    return img


def draw_card(img, item, idx, n, progress):
    p = r.ease(progress)
    layer = Image.new("RGBA", (r.W, 340), (0, 0, 0, 0))
    d = k.draw(layer)
    d.rounded_rectangle((r.SAFE_LEFT, 0, r.SAFE_RIGHT, 330), radius=36, fill=CARD + (255,))
    k.center_text(d, 62, f"{idx + 1} OF {n}", r.BOLD, 40, (220, 170, 205))
    f, lines = k.wrap(d, item.upper(), r.BOLD, 96, r.SAFE_RIGHT - r.SAFE_LEFT - 80, max_lines=2, min_size=50)
    lh = f.size * 1.1
    y = 190 - (len(lines) - 1) * lh / 2
    for ln in lines:
        d.text(((r.SAFE_LEFT + r.SAFE_RIGHT) / 2, y), ln, font=f, fill=r.WHITE, anchor="mm")
        y += lh
    scale = 0.85 + 0.15 * p
    layer = layer.resize((int(r.W * scale), int(340 * scale)))
    if p < 1:
        layer.putalpha(layer.getchannel("A").point(lambda a: int(a * p)))
    img.paste(layer, (int((r.W - layer.width) / 2), 575 + int((340 - layer.height) / 2)), layer)


def draw_slots(img, items, shown):
    d = k.draw(img)
    top, h = 950, 96
    for i in range(len(items)):
        y = top + i * h
        d.rounded_rectangle((r.SAFE_LEFT, y, r.SAFE_RIGHT, y + h - 14), radius=24, fill=ROW_BG)
        label = items[i].upper() if i < shown else "? ? ?"
        col = r.WHITE if i < shown else (120, 80, 110)
        d.text((r.SAFE_LEFT + 30, y + (h - 14) / 2), label, font=r.fit_font(d, label, r.BOLD, 46, r.SAFE_RIGHT - r.SAFE_LEFT - 60),
               fill=col, anchor="lm")


def plan(rset):
    items = rset["items"]
    intro = k.voice(f"Blind rank these {rset.get('say', rset['topic'].lower())}. No changing your answer.")
    t = max(1.3, k.clip_len(intro) + 0.15)
    steps = []
    for it in items:
        clip = k.voice(it)
        steps.append({"start": t, "clip": clip})
        t += max(1.9, k.clip_len(clip) + 1.1)   # Zeit zum Einordnen
    end = k.voice("Comment your ranking.")
    return {"intro": intro, "steps": steps, "end_at": t, "end": end, "total": t + max(2.4, k.clip_len(end) + 0.8)}


def render_rank(rset, out_path):
    p = plan(rset)
    items = rset["items"]
    n = len(items)
    base = header(rset)

    def frame(t):
        img = base.copy()
        cur = max([i for i, s in enumerate(p["steps"]) if s["start"] <= t], default=-1)
        if t < p["end_at"]:
            draw_slots(img, items, cur + 1 if cur >= 0 else 0)
            if cur >= 0:
                draw_card(img, items[cur], cur, n, (t - p["steps"][cur]["start"]) / 0.25)
            else:
                d = k.draw(img)
                k.center_text(d, 745, "READY?", r.BOLD, 110, r.WHITE)
        else:
            draw_slots(img, items, n)
            d = k.draw(img)
            q = r.ease((t - p["end_at"]) / 0.35)
            d.rounded_rectangle((r.SAFE_LEFT, 575, r.SAFE_RIGHT, 905), radius=36, fill=ACCENT)
            k.center_text(d, 700, "COMMENT YOUR", r.BOLD, int(70 + 8 * q), BOTTOM)
            k.center_text(d, 800, "RANKING 1-5", r.BOLD, int(90 + 10 * q), BOTTOM)
        return img

    audio = k.silence(p["total"])
    k.add_pulse(audio, bpm=124, volume=0.1, end=p["end_at"])
    k.add_clip(audio, 0.05, p["intro"])
    for i, s in enumerate(p["steps"]):
        k.add_tone(audio, s["start"], 600 + 50 * i, 0.14, 0.22)
        k.add_clip(audio, s["start"] + 0.08, s["clip"])
    for freq in (392.0, 523.25, 659.25):
        k.add_tone(audio, p["end_at"], freq, 1.2, 0.15)
    k.add_clip(audio, p["end_at"] + 0.1, p["end"])
    k.encode(out_path, p["total"], frame, audio)
    return {"path": out_path, "duration": p["total"], "thumb_ms": int((p["steps"][0]["start"] + 0.5) * 1000),
            "voice": p["intro"] is not None}


if __name__ == "__main__":
    sets = {s["id"]: s for s in load_sets()}
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "out", "rank.mp4")
    print(render_rank(sets[sys.argv[1]], out))
