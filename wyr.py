"""Experiment 17.11. nachmittags: "Would you rather" (Format wyr).

Recherche 17.11.: kurze (7-15 s) Text-Reels mit Neugier-/Entscheidungsfrage ohne Vorwissen,
Hook schon im ersten Bild (kein Vorspann), Loop-faehig, eigene Tonspur statt fremder Musik.
Beide Optionen stehen ab Frame 0 im Bild (rot oben, blau unten), die KI-Stimme liest die
Frage vor, dann 3-2-1 und "COMMENT RED OR BLUE". Keine erfundenen Abstimmungs-Prozente.
Themen: allgemein (breites Publikum) und Fussball.

Aufruf:  python wyr.py <set-id> [ausgabe.mp4] [--frame]
"""
import json
import os
import sys

import reelkit as k
import render as r

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data", "wyr.json")
RED_TOP, RED_BOTTOM = (214, 40, 64), (120, 14, 34)
BLUE_TOP, BLUE_BOTTOM = (36, 108, 230), (12, 40, 120)
MID = r.H // 2
MIN_READ = 3.4     # Mindestzeit fuer die Frage, falls keine Stimme verfuegbar ist
COUNT = 1.8        # 3-2-1
END_HOLD = 1.2     # "COMMENT RED OR BLUE", danach Loop
CAPTIONS = [
    "Red or blue? Comment your pick, then send this to a friend and see if they agree.",
    "There is no right answer. Red or blue? Comment it and send this to the person who'd pick the opposite.",
    "Be honest. Red or blue? Comment and send this to your group chat to start the debate.",
]


def load_sets():
    with open(DATA, encoding="utf-8") as f:
        return json.load(f)


def _half(top, bottom, h):
    img = k.gradient(top, bottom)
    return img.crop((0, 0, r.W, h))


def base_frame(wset):
    from PIL import Image
    img = Image.new("RGB", (r.W, r.H))
    img.paste(_half(RED_TOP, RED_BOTTOM, MID), (0, 0))
    img.paste(_half(BLUE_TOP, BLUE_BOTTOM, r.H - MID), (0, MID))
    d = k.draw(img)
    width = r.SAFE_RIGHT - r.SAFE_LEFT
    # Hook ab Frame 0
    k.center_text(d, 210, "WOULD YOU RATHER", r.BOLD, 82, r.WHITE, width)
    for y_mid, text in ((MID // 2 + 60, wset["red"]), (MID + (r.H - MID) // 2 - 40, wset["blue"])):
        f, lines = k.wrap(d, text.upper(), r.BOLD, 84, width - 40, max_lines=4, min_size=46)
        lh = f.size * 1.15
        y = y_mid - (len(lines) - 1) * lh / 2
        for ln in lines:
            d.text(((r.SAFE_LEFT + r.SAFE_RIGHT) / 2, y), ln, font=f, fill=r.WHITE, anchor="mm")
            y += lh
    # "OR"-Kreis in der Mitte
    d.ellipse((r.W / 2 - 80, MID - 80, r.W / 2 + 80, MID + 80), fill=r.WHITE)
    d.text((r.W / 2, MID), "OR", font=r.font(r.BOLD, 66), fill=(20, 20, 30), anchor="mm")
    return img


def plan(clip):
    read = max(MIN_READ, k.clip_len(clip) + 0.3)
    return {"read": read, "count_end": read + COUNT, "total": read + COUNT + END_HOLD}


def render_wyr(wset, out_path):
    clip = k.voice(f"Would you rather {wset['red']}... or {wset['blue']}?")
    p = plan(clip)
    base = base_frame(wset)

    def frame(t):
        if t < p["read"]:
            return base
        img = base.copy()
        d = k.draw(img)
        if t < p["count_end"]:
            n = 3 - int((t - p["read"]) / (COUNT / 3))
            d.ellipse((r.W / 2 - 80, MID - 80, r.W / 2 + 80, MID + 80), fill=(255, 214, 0))
            d.text((r.W / 2, MID), str(max(n, 1)), font=r.font(r.BOLD, 96), fill=(20, 20, 30), anchor="mm")
        else:
            d.rounded_rectangle((r.SAFE_LEFT, MID - 86, r.SAFE_RIGHT, MID + 86), radius=86, fill=r.WHITE)
            k.center_text(d, MID, "COMMENT RED OR BLUE", r.BOLD, 70, (20, 20, 30), r.SAFE_RIGHT - r.SAFE_LEFT - 60)
        return img

    audio = k.silence(p["total"])
    k.add_pulse(audio, volume=0.08)
    k.add_clip(audio, 0.05, clip)
    for i in range(3):
        k.add_tone(audio, p["read"] + i * COUNT / 3, 660 + 110 * i, 0.18, 0.25)
    k.add_tone(audio, p["count_end"], 990, 0.6, 0.25)
    k.encode(out_path, p["total"], frame, audio)
    return {"path": out_path, "duration": p["total"], "thumb_ms": 300, "voice": clip is not None}


if __name__ == "__main__":
    sets = {s["id"]: s for s in load_sets()}
    wset = sets[sys.argv[1]]
    if "--frame" in sys.argv:
        os.makedirs(os.path.join(ROOT, "out"), exist_ok=True)
        base_frame(wset).save(os.path.join(ROOT, "out", "wyr.png"))
    else:
        print(render_wyr(wset, sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "out", "wyr.mp4")))
