"""Format "facts" (ab 17.11.): nummerierte Liste, die sich Zeile fuer Zeile fuellt (#5 -> #1),
mit KI-Stimme, die jede Zeile vorliest. Vorbild: die meistgesehenen Faceless-Reels sind
Listen mit einem Versprechen in Zeile 1 ("#1 is insane") und einem Grund, bis zum Ende zu schauen.

Aufruf:  python facts.py <set-id> [ausgabe.mp4] [--frame]
"""
import json
import os
import sys

from PIL import Image

import reelkit as k
import render as r

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data", "facts.json")
ACCENT = (255, 196, 0)       # eigenes Gelb, damit sich das Format vom Quiz abhebt
TOP, BOTTOM = (34, 14, 44), (8, 4, 16)
ROW_BG = (52, 26, 66)
LIST_TOP, LIST_BOTTOM = 560, 1420
ANIM = 0.3
END_HOLD = 2.6
CAPTIONS = [
    "Number 1 sounds made up, but it's 100% true. Which one did you know? Send this to someone who won't believe it.",
    "Be honest, how many did you know? Comment the number and send this to a friend.",
    "I didn't believe number 1 either. Send this to the smartest person you know.",
]


def load_sets():
    with open(DATA, encoding="utf-8") as f:
        return json.load(f)


def header(fset):
    img = k.gradient(TOP, BOTTOM)
    d = k.draw(img)
    width = r.SAFE_RIGHT - r.SAFE_LEFT
    d.text((r.SAFE_LEFT, 236), fset["title"][0], font=r.fit_font(d, fset["title"][0], r.BOLD, 76, width), fill=r.WHITE)
    d.text((r.SAFE_LEFT, 318), fset["title"][1], font=r.fit_font(d, fset["title"][1], r.BOLD, 112, width), fill=ACCENT)
    hook = fset.get("hook", "#1 IS INSANE")
    f = r.fit_font(d, hook, r.BOLD, 44, width)
    tw = d.textlength(hook, font=f)
    d.rounded_rectangle((r.SAFE_LEFT, 452, r.SAFE_LEFT + tw + 50, 516), radius=32, fill=(255, 70, 90))
    d.text((r.SAFE_LEFT + 25, 484), hook, font=f, fill=r.WHITE, anchor="lm")
    n = len(fset["facts"])
    row_h = (LIST_BOTTOM - LIST_TOP) / n
    for i in range(n):  # leere, nummerierte Platzhalter -> Zuschauer sieht, dass noch etwas kommt
        y0 = LIST_TOP + i * row_h
        d.rounded_rectangle((r.SAFE_LEFT, y0, r.SAFE_LEFT + 100, y0 + row_h - 18), radius=24, fill=ROW_BG)
        d.text((r.SAFE_LEFT + 50, y0 + (row_h - 18) / 2), str(i + 1), font=r.font(r.BOLD, 56), fill=ACCENT, anchor="mm")
    k.pill(d, 1507, fset.get("share", "SEND THIS TO SOMEONE WHO WON'T BELIEVE IT"), ACCENT, BOTTOM, 46)
    return img


def draw_row(img, slot, n, text, progress):
    row_h = (LIST_BOTTOM - LIST_TOP) / n
    box_h = int(row_h - 18)
    y0 = int(LIST_TOP + slot * row_h)
    p = r.ease(progress)
    layer = Image.new("RGBA", (r.W, box_h + 2), (0, 0, 0, 0))
    d = k.draw(layer)
    x0 = r.SAFE_LEFT + 116
    d.rounded_rectangle((x0, 0, r.SAFE_RIGHT, box_h), radius=24, fill=ROW_BG + (255,))
    f, lines = k.wrap(d, text, r.BOLD, 42, r.SAFE_RIGHT - x0 - 40, max_lines=3)
    lh = f.size * 1.18
    y = box_h / 2 - (len(lines) - 1) * lh / 2
    for ln in lines:
        d.text((x0 + 22, y), ln, font=f, fill=r.WHITE, anchor="lm")
        y += lh
    if p < 1:
        layer.putalpha(layer.getchannel("A").point(lambda a: int(a * p)))
    img.paste(layer, (int((1 - p) * 90), y0), layer)


def plan(fset):
    """Zeitplan + Stimme. Reihenfolge der Einblendung: #5 zuerst (unterste Zeile), #1 zuletzt."""
    facts = fset["facts"]
    n = len(facts)
    intro_clip = k.voice(fset.get("say", "These facts sound fake, but they are all true."))
    t = max(1.2, k.clip_len(intro_clip) + 0.15)
    steps = []
    for idx in range(n):
        slot = n - 1 - idx          # #5 ... #1
        clip = k.voice(f"Number {slot + 1}. " + facts[slot])
        words = len(facts[slot].split())
        dur = max(2.2, k.clip_len(clip) + 0.15) if clip is not None else max(2.4, 0.3 * words)
        steps.append({"slot": slot, "start": t, "clip": clip})
        t += dur
    end_clip = k.voice("Which one did you know? Comment the number.")
    return {"intro": intro_clip, "steps": steps, "end_at": t, "end_clip": end_clip,
            "total": t + max(END_HOLD, k.clip_len(end_clip) + 0.6)}


def render_facts(fset, out_path):
    p = plan(fset)
    n = len(fset["facts"])
    base = header(fset)
    state = {"done": set()}

    def frame(t):
        for s in p["steps"]:
            if t >= s["start"] + ANIM and s["slot"] not in state["done"]:
                draw_row(base, s["slot"], n, fset["facts"][s["slot"]], 1.0)
                state["done"].add(s["slot"])
        img = base.copy()
        for s in p["steps"]:
            if s["start"] <= t < s["start"] + ANIM:
                draw_row(img, s["slot"], n, fset["facts"][s["slot"]], (t - s["start"]) / ANIM)
        if t >= p["end_at"]:
            d = k.draw(img)
            q = r.ease((t - p["end_at"]) / 0.35)
            k.center_text(d, 1650, "WHICH ONE DID YOU KNOW?", r.BOLD, int(56 + 12 * q), r.WHITE)
        return img

    audio = k.silence(p["total"])
    k.add_pulse(audio, end=p["end_at"])
    k.add_clip(audio, 0.05, p["intro"])
    for i, s in enumerate(p["steps"]):
        k.add_tone(audio, s["start"], 480 + 60 * i, 0.15, 0.22)
        k.add_clip(audio, s["start"] + 0.05, s["clip"])
    for freq in (392.0, 523.25, 659.25):
        k.add_tone(audio, p["end_at"], freq, 1.2, 0.15)
    k.add_clip(audio, p["end_at"] + 0.1, p["end_clip"])
    k.encode(out_path, p["total"], frame, audio)
    voiced = p["intro"] is not None
    return {"path": out_path, "duration": p["total"], "thumb_ms": int((p["end_at"] + 0.4) * 1000), "voice": voiced}


if __name__ == "__main__":
    sets = {s["id"]: s for s in load_sets()}
    fset = sets[sys.argv[1]]
    out = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else os.path.join(ROOT, "out", "facts.mp4")
    print(render_facts(fset, out))
