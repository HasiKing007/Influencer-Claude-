"""Format "odd" (ab 17.11.): "Find the odd one out" Suchbild-Raetsel.
Raster aus gleichen Zeichen, eines ist anders. Countdown, dann wird es markiert.
Breites Publikum (kein Fussballwissen noetig), Leute schauen mehrfach (Loops) und
kommentieren ihre Zeit ("found it in 2 sec"). Komplett prozedural -> unbegrenzter Vorrat.

Aufruf:  python odd.py <seed> [ausgabe.mp4]
"""
import os
import random
import sys

import reelkit as k
import render as r

ACCENT = (0, 220, 255)
TOP, BOTTOM = (6, 26, 40), (2, 8, 14)
COLS, ROWS = 10, 14
GRID_TOP, GRID_BOTTOM = 560, 1420
SEARCH = 6.0      # Sekunden Suchzeit
REVEAL = 2.2
# (normal, anders, Schwierigkeit) - DejaVu Bold, alles gut lesbar
PAIRS = [("8", "B", "HARD"), ("O", "Q", "MEDIUM"), ("M", "N", "MEDIUM"), ("E", "F", "HARD"),
         ("5", "S", "HARD"), ("P", "R", "MEDIUM"), ("V", "U", "MEDIUM"), ("b", "d", "HARD"),
         ("W", "VV", None), ("6", "9", "MEDIUM"), ("3", "8", "MEDIUM"), ("I", "1", "HARD"),
         ("C", "G", "HARD"), ("q", "g", "HARD"), ("X", "K", "MEDIUM"), ("Z", "2", "HARD")]
PAIRS = [p for p in PAIRS if p[2]]
HOOKS = ["ONLY 1 IN 10 FIND IT", "99% CAN'T FIND IT", "FIND IT IN 6 SECONDS", "YOUR BRAIN WILL MISS IT"]
CAPTIONS = [
    "Did you find the {odd}? Comment how many seconds you needed, then send this to a friend and time them.",
    "Most people can't find the {odd} in 6 seconds. Be honest, did you? Send it to someone and see who's faster.",
    "Found the {odd}? Comment the row number. Then send this to a friend who thinks they have sharp eyes.",
]
TAGS = "#puzzle #findtheoddone #braintest #riddle #eyetest"


def setup(seed):
    rng = random.Random(seed)
    normal, odd, level = PAIRS[seed % len(PAIRS)]
    pos = (rng.randrange(1, COLS - 1), rng.randrange(1, ROWS - 1))   # nie ganz am Rand
    return {"normal": normal, "odd": odd, "level": level, "pos": pos,
            "hook": HOOKS[(seed // len(PAIRS)) % len(HOOKS)], "seed": seed}


def cell_center(c, rr):
    cw = (r.SAFE_RIGHT - r.SAFE_LEFT) / COLS
    ch = (GRID_BOTTOM - GRID_TOP) / ROWS
    return r.SAFE_LEFT + cw * (c + 0.5), GRID_TOP + ch * (rr + 0.5), cw, ch


def base_image(cfg):
    img = k.gradient(TOP, BOTTOM)
    d = k.draw(img)
    width = r.SAFE_RIGHT - r.SAFE_LEFT
    d.text((r.SAFE_LEFT, 236), cfg["hook"], font=r.fit_font(d, cfg["hook"], r.BOLD, 76, width), fill=r.WHITE)
    title = f"FIND THE {cfg['odd']}"
    d.text((r.SAFE_LEFT, 318), title, font=r.fit_font(d, title, r.BOLD, 120, width), fill=ACCENT)
    lvl = f"LEVEL: {cfg['level']}"
    f = r.font(r.BOLD, 40)
    tw = d.textlength(lvl, font=f)
    d.rounded_rectangle((r.SAFE_LEFT, 458, r.SAFE_LEFT + tw + 44, 516), radius=29, fill=(255, 70, 90))
    d.text((r.SAFE_LEFT + 22, 487), lvl, font=f, fill=r.WHITE, anchor="lm")
    gf = r.font(r.BOLD, 54)
    for rr in range(ROWS):
        for c in range(COLS):
            ch = cfg["odd"] if (c, rr) == cfg["pos"] else cfg["normal"]
            x, y, _, _ = cell_center(c, rr)
            d.text((x, y), ch, font=gf, fill=r.WHITE, anchor="mm")
    k.pill(d, 1507, "SEND THIS TO A FRIEND AND TIME THEM", ACCENT, BOTTOM, 48)
    return img


def frame_at(t, cfg, base):
    img = base.copy()
    d = k.draw(img)
    if t < SEARCH:
        left = SEARCH - t
        frac = left / SEARCH
        x1 = r.SAFE_LEFT + (r.SAFE_RIGHT - r.SAFE_LEFT) * frac
        col = ACCENT if left > 2 else (255, 70, 90)
        d.rounded_rectangle((r.SAFE_LEFT, 1600, r.SAFE_RIGHT, 1630), radius=15, fill=(30, 44, 60))
        if x1 > r.SAFE_LEFT + 30:
            d.rounded_rectangle((r.SAFE_LEFT, 1600, x1, 1630), radius=15, fill=col)
        k.center_text(d, 1700, f"{int(left) + 1}", r.BOLD, 80, col)
    else:
        p = r.ease((t - SEARCH) / 0.4)
        x, y, cw, ch = cell_center(*cfg["pos"])
        rad = max(cw, ch) * (0.55 + 1.2 * (1 - p))
        d.ellipse((x - rad, y - rad, x + rad, y + rad), outline=(255, 70, 90), width=10)
        k.center_text(d, 1650, f"ROW {cfg['pos'][1] + 1}. DID YOU GET IT?", r.BOLD, 60, r.WHITE)
    return img


def render_odd(seed, out_path):
    cfg = setup(seed)
    base = base_image(cfg)
    total = SEARCH + REVEAL
    intro = k.voice(f"Find the {cfg['odd'].upper() if cfg['odd'].isalpha() else cfg['odd']}. You have six seconds.")
    outro = k.voice("Did you find it? Comment your time.")
    audio = k.silence(total)
    k.add_clip(audio, 0.05, intro)
    for s in range(int(SEARCH)):
        k.add_tick(audio, s, 0.35 if SEARCH - s <= 3 else 0.22)
    k.add_pulse(audio, bpm=100, volume=0.08, end=SEARCH)
    for freq in (523.25, 659.25, 783.99):
        k.add_tone(audio, SEARCH, freq, 1.0, 0.18)
    k.add_clip(audio, SEARCH + 0.4, outro)
    k.encode(out_path, total, lambda t: frame_at(t, cfg, base), audio)
    cfg["path"], cfg["duration"] = out_path, total
    cfg["thumb_ms"] = 1500
    cfg["voice"] = intro is not None
    return cfg


if __name__ == "__main__":
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else random.randint(1, 10 ** 6)
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "odd.mp4")
    print({kk: v for kk, v in render_odd(seed, out).items()})
