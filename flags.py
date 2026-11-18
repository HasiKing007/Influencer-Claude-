"""Experiment 18.11. nachmittags: "Guess the flag" (Format flags).

Recherche 18.11.: Instagram stuft Reels, die ueberwiegend aus Text bestehen, als weniger
empfehlenswert ein (creators.instagram.com, Recommendations & Originality); alle bisherigen
Formate sind fast reine Text-Reels. Quiz-Kanaele mit visuellen Raetseln (Flaggen, Emojis)
erreichen Millionen Views. Daher: ein Format, bei dem ein grosses Bild (selbst gezeichnete
Nationalflagge, gemeinfreie Symbole, keine Logos/Fotos) den Bildschirm fuellt und kaum Text steht.

Ablauf (~10 s, Loop): 4 Flaggen mit steigender Schwierigkeit (EASY -> IMPOSSIBLE), je 2 s mit
ablaufendem Timer-Balken, danach Aufloesung als 2x2-Raster mit Namen und "COMMENT YOUR SCORE".
KI-Stimme sagt nur den Hook.

Aufruf:  python flags.py <set-id> [ausgabe.mp4] [--frame]
"""
import json
import os
import sys

from PIL import Image

import reelkit as k
import render as r

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data", "flags.json")

PER_FLAG = 2.0
REVEAL = 2.6
LEVELS = [("EASY", (60, 200, 110)), ("MEDIUM", (250, 200, 40)), ("HARD", (250, 130, 40)), ("IMPOSSIBLE", (235, 50, 70))]
BG_TOP, BG_BOTTOM = (18, 24, 52), (6, 8, 20)
DARK = (14, 16, 30)

# Farben (gerundete Standardwerte)
C = {
    "red": (206, 17, 38), "white": (255, 255, 255), "blue": (0, 57, 166), "black": (0, 0, 0),
    "gold": (255, 206, 0), "yellow": (252, 209, 22), "green": (0, 135, 81), "orange": (255, 130, 0),
    "lightblue": (0, 161, 222), "navy": (0, 38, 100), "sky": (75, 160, 230),
}

# Flaggen aus einfachen Formen. h = waagrechte Streifen (oben->unten), v = senkrechte (links->rechts),
# Gewichte optional. nordic = Skandinavisches Kreuz, disc = Scheibe, czech = Keil.
FLAGS = {
    "germany": ("h", ["black", "red", "gold"]),
    "austria": ("h", ["red", "white", "red"]),
    "netherlands": ("h", ["red", "white", "blue"]),
    "russia": ("h", ["white", "blue", "red"]),
    "hungary": ("h", ["red", "white", "green"]),
    "bulgaria": ("h", ["white", "green", "red"]),
    "estonia": ("h", ["lightblue", "black", "white"]),
    "lithuania": ("h", ["yellow", "green", "red"]),
    "luxembourg": ("h", ["red", "white", "lightblue"]),
    "yemen": ("h", ["red", "white", "black"]),
    "sierra leone": ("h", ["green", "white", "lightblue"]),
    "gabon": ("h", ["green", "yellow", "blue"]),
    "armenia": ("h", ["red", "blue", "orange"]),
    "colombia": ("h", ["yellow", "blue", "red"], [2, 1, 1]),
    "ukraine": ("h", ["blue", "yellow"]),
    "poland": ("h", ["white", "red"]),
    "thailand": ("h", ["red", "white", "navy", "white", "red"], [1, 1, 2, 1, 1]),
    "france": ("v", ["blue", "white", "red"]),
    "italy": ("v", ["green", "white", "red"]),
    "ireland": ("v", ["green", "white", "orange"]),
    "belgium": ("v", ["black", "yellow", "red"]),
    "romania": ("v", ["blue", "yellow", "red"]),
    "mali": ("v", ["green", "yellow", "red"]),
    "guinea": ("v", ["red", "yellow", "green"]),
    "nigeria": ("v", ["green", "white", "green"]),
    "peru": ("v", ["red", "white", "red"]),
    "ivory coast": ("v", ["orange", "white", "green"]),
    "sweden": ("nordic", "lightblue", "yellow", None),
    "denmark": ("nordic", "red", "white", None),
    "finland": ("nordic", "white", "blue", None),
    "norway": ("nordic", "red", "white", "navy"),
    "iceland": ("nordic", "blue", "white", "red"),
    "japan": ("disc", "white", "red", 0.5, 0.3),
    "bangladesh": ("disc", "green", "red", 0.45, 0.33),
    "palau": ("disc", "sky", "yellow", 0.44, 0.3),
    "czechia": ("czech",),
}


def load_sets():
    with open(DATA, encoding="utf-8") as f:
        return json.load(f)


def draw_flag(name, w, h):
    spec = FLAGS[name]
    img = Image.new("RGB", (w, h), C["white"])
    d = k.draw(img)
    kind = spec[0]
    if kind in ("h", "v"):
        cols = spec[1]
        weights = spec[2] if len(spec) > 2 else [1] * len(cols)
        total, pos = sum(weights), 0
        size = h if kind == "h" else w
        for col, wt in zip(cols, weights):
            a, b = round(pos / total * size), round((pos + wt) / total * size)
            d.rectangle((0, a, w, b) if kind == "h" else (a, 0, b, h), fill=C[col])
            pos += wt
    elif kind == "nordic":
        _, field, cross, inner = spec
        d.rectangle((0, 0, w, h), fill=C[field])
        cx, cy = 0.375 * w, h / 2
        t = (0.25 if inner else 0.2) * h / 2
        d.rectangle((cx - t, 0, cx + t, h), fill=C[cross])
        d.rectangle((0, cy - t, w, cy + t), fill=C[cross])
        if inner:
            t2 = 0.125 * h / 2
            d.rectangle((cx - t2, 0, cx + t2, h), fill=C[inner])
            d.rectangle((0, cy - t2, w, cy + t2), fill=C[inner])
    elif kind == "disc":
        _, field, disc, fx, fr = spec
        d.rectangle((0, 0, w, h), fill=C[field])
        cx, rad = fx * w, fr * h
        d.ellipse((cx - rad, h / 2 - rad, cx + rad, h / 2 + rad), fill=C[disc])
    elif kind == "czech":
        d.rectangle((0, 0, w, h / 2), fill=C["white"])
        d.rectangle((0, h / 2, w, h), fill=C["red"])
        d.polygon([(0, 0), (w / 2, h / 2), (0, h)], fill=(17, 69, 126))
    return img


def framed(name, w, h):
    """Flagge mit hellem Rahmen (damit weisse Flaggenteile auf dunklem Grund sichtbar bleiben)."""
    pad = max(4, w // 90)
    out = Image.new("RGB", (w + 2 * pad, h + 2 * pad), (200, 205, 220))
    out.paste(draw_flag(name, w, h), (pad, pad))
    return out


def background():
    return k.gradient(BG_TOP, BG_BOTTOM)


FW, FH = 820, 547
CX = (r.SAFE_LEFT + r.SAFE_RIGHT) // 2   # Flagge in der sicheren Zone (rechts liegen die IG-Buttons)
FY = 640


def flag_frame(fset, i, frac_left, bg):
    img = bg.copy()
    d = k.draw(img)
    width = r.SAFE_RIGHT - r.SAFE_LEFT
    k.pill(d, 230, "GUESS THE FLAG", r.WHITE, DARK, size=66, h=112)
    k.center_text(d, 350, "CAN YOU GET 4/4?", r.BOLD, 54, (190, 200, 235), width)
    label, col = LEVELS[i]
    k.center_text(d, FY - 90, f"{i + 1}/4  {label}", r.BOLD, 64, col, width)
    fl = framed(fset["flags"][i], FW, FH)
    img.paste(fl, (CX - fl.width // 2, FY))
    # Timer-Balken
    y = FY + fl.height + 50
    x0, x1 = CX - FW // 2, CX + FW // 2
    d.rounded_rectangle((x0, y, x1, y + 26), radius=13, fill=(40, 46, 80))
    d.rounded_rectangle((x0, y, x0 + max(26, (x1 - x0) * frac_left), y + 26), radius=13, fill=col)
    k.pill(d, 1560, "COMMENT YOUR SCORE", r.WHITE, DARK, size=54, h=100)
    return img


def reveal_frame(fset, bg):
    img = bg.copy()
    d = k.draw(img)
    width = r.SAFE_RIGHT - r.SAFE_LEFT
    k.pill(d, 230, "ANSWERS", (250, 200, 40), DARK, size=66, h=112)
    w, h = 380, 253
    for i, name in enumerate(fset["flags"]):
        cx = CX + (-215 if i % 2 == 0 else 215)
        top = 400 + (i // 2) * 470
        fl = framed(name, w, h)
        img.paste(fl, (cx - fl.width // 2, top))
        f = r.fit_font(d, name.upper(), r.BOLD, 50, 410)
        d.text((cx, top + fl.height + 50), name.upper(), font=f, fill=LEVELS[i][1], anchor="mm")
    k.pill(d, 1450, "HOW MANY DID YOU GET?", r.WHITE, DARK, size=54, h=100)
    k.center_text(d, 1580, "COMMENT YOUR SCORE /4", r.BOLD, 56, (190, 200, 235), width)
    return img


def render_flags(fset, out_path):
    clip = k.voice("Guess all four flags. Number four is almost impossible. Comment your score!")
    total = 4 * PER_FLAG + REVEAL
    bg = background()
    rev = reveal_frame(fset, bg)
    cache = {}

    def frame(t):
        if t >= 4 * PER_FLAG:
            return rev
        i = int(t / PER_FLAG)
        frac = 1 - (t - i * PER_FLAG) / PER_FLAG
        key = (i, round(frac * 30))
        if key not in cache:
            cache.clear()
            cache[key] = flag_frame(fset, i, frac, bg)
        return cache[key]

    audio = k.silence(total)
    k.add_pulse(audio, volume=0.08)
    k.add_clip(audio, 0.05, clip)
    for i in range(4):
        k.add_tone(audio, i * PER_FLAG, 520 + 90 * i, 0.25, 0.22)
        for j in range(1, 4):
            k.add_tick(audio, i * PER_FLAG + j * PER_FLAG / 4, 0.18)
    k.add_tone(audio, 4 * PER_FLAG, 990, 0.7, 0.28)
    k.encode(out_path, total, frame, audio)
    return {"path": out_path, "duration": total, "thumb_ms": 300, "voice": clip is not None}


CAPTIONS = [
    "How many did you get? Comment your score out of 4 and send this to the friend who thinks they know geography.",
    "Be honest: how many flags did you get? Comment your score, then send it to someone who will get fewer.",
    "4/4 or nothing. Comment your score and tag the geography nerd in your group chat.",
]

TAGS = "#guesstheflag #flags #geography #quiz #trivia"


if __name__ == "__main__":
    sets = {s["id"]: s for s in load_sets()}
    fset = sets[sys.argv[1]]
    if "--frame" in sys.argv:
        os.makedirs(os.path.join(ROOT, "out"), exist_ok=True)
        bg = background()
        flag_frame(fset, 3, 0.6, bg).save(os.path.join(ROOT, "out", "flags.png"))
        reveal_frame(fset, bg).save(os.path.join(ROOT, "out", "flags_reveal.png"))
    else:
        print(render_flags(fset, sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "out", "flags.mp4")))
