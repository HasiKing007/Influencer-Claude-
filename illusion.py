"""Experiment 18.11. abends: Nachbild-Illusion "Stare at the dot" (Format illusion).

Recherche 18.11. abends: Illusions-/"wie geht das"-Reels werden mehrfach angesehen, um den Effekt
nochmal zu erleben (anijam.ai, Beispiel ~4 Mio. Views); Loops unter 15 s mit "nochmal schauen"-Grund
(joyspace.ai); Instagram empfiehlt ueberwiegende Text-Reels seltener (creators.instagram.com).
Daher ein reines Bild-Erlebnis ohne Vorwissen: Man starrt 8 s auf eine Flagge in Komplementaerfarben,
dann wird der Schirm hell und das Auge "sieht" die echte Flagge (negatives Nachbild, klassischer
Wahrnehmungseffekt). Die Flagge wird nie in echten Farben gezeigt: Wer sie erkennen will, muss
mitmachen, wer sie verpasst, schaut nochmal (Loop). Kommentar-Aufgabe: Land nennen.

Flaggen selbst gezeichnet (flags.py), keine Logos/Fotos. Ton: eigener Synth + KI-Stimme (edge-tts).

Aufruf:  python illusion.py <set-id> [ausgabe.mp4] [--frame]
"""
import json
import os
import sys

from PIL import ImageOps

import flags as fl
import reelkit as k
import render as r

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data", "illusions.json")

STARE = 8.0
AFTER = 4.6
GREY = (190, 190, 190)     # Umgebung beim Starren (neutral, erzeugt selbst kein farbiges Nachbild)
LIGHT = (236, 236, 236)    # heller Schirm fuer das Nachbild
INK = (25, 25, 35)
FW, FH = 860, 573
CX = (r.SAFE_LEFT + r.SAFE_RIGHT) // 2
FY = 660
DOT = (CX, FY + FH // 2)


def load_sets():
    with open(DATA, encoding="utf-8") as f:
        return json.load(f)


def _dot(d, rad=13):
    d.ellipse((DOT[0] - rad, DOT[1] - rad, DOT[0] + rad, DOT[1] + rad), fill=(0, 0, 0))


def stare_frame(iset, secs_left):
    img = k.gradient(GREY, GREY)
    d = k.draw(img)
    k.center_text(d, 260, "STARE AT THE BLACK DOT", r.BOLD, 70, INK)
    k.center_text(d, 360, "DON'T MOVE YOUR EYES", r.BOLD, 52, (90, 20, 30))
    k.center_text(d, 450, "UNTIL THE SCREEN TURNS WHITE", r.BOLD, 44, (60, 60, 75))
    neg = ImageOps.invert(fl.draw_flag(iset["flag"], FW, FH))
    img.paste(neg, (CX - FW // 2, FY))
    _dot(d)
    k.center_text(d, FY + FH + 120, str(max(1, int(secs_left + 0.999))), r.BOLD, 120, INK)
    return img


def after_frame(t_after):
    img = k.gradient(LIGHT, LIGHT)
    d = k.draw(img)
    k.center_text(d, 300, "KEEP LOOKING AT THE DOT", r.BOLD, 62, (120, 120, 130))
    _dot(d, 10)
    if t_after > 2.2:
        k.center_text(d, 420, "WHICH FLAG DO YOU SEE?", r.BOLD, 64, INK)
        k.pill(d, 1560, "COMMENT THE COUNTRY", INK, (245, 245, 245), size=54, h=100)
    return img


def render_illusion(iset, out_path):
    hook = k.voice("Stare at the black dot for eight seconds. Don't move your eyes.")
    now = k.voice("Now keep looking. Which flag do you see?")
    total = STARE + AFTER
    cache = {}

    def frame(t):
        key = ("s", int(STARE - t + 0.999)) if t < STARE else ("a", t - STARE > 2.2)
        if key not in cache:
            cache.clear()
            cache[key] = stare_frame(iset, STARE - t) if t < STARE else after_frame(t - STARE)
        return cache[key]

    audio = k.silence(total)
    k.add_pulse(audio, bpm=60, volume=0.06, end=STARE)
    k.add_clip(audio, 0.05, hook)
    for s in range(1, int(STARE)):
        k.add_tick(audio, s, 0.16)
    k.add_tone(audio, STARE, 880, 0.8, 0.3)
    k.add_clip(audio, STARE + 0.25, now)
    k.encode(out_path, total, frame, audio)
    return {"path": out_path, "duration": total, "thumb_ms": 300,
            "voice": hook is not None and now is not None}


CAPTIONS = [
    "Stare at the dot until the screen turns white. Which flag did you see? Comment the country, then send this to a friend and see if they get it too.",
    "Your eyes will see a flag that is not there. Comment which country you saw (no cheating) and send this to someone who needs to try it.",
    "This only works if you don't move your eyes. Comment the country you saw. Didn't work? Watch again.",
]

TAGS = "#illusion #opticalillusion #brain #flags #mindblown"


if __name__ == "__main__":
    sets = {s["id"]: s for s in load_sets()}
    iset = sets[sys.argv[1]]
    if "--frame" in sys.argv:
        os.makedirs(os.path.join(ROOT, "out"), exist_ok=True)
        stare_frame(iset, 5.5).save(os.path.join(ROOT, "out", "illusion.png"))
        after_frame(3.0).save(os.path.join(ROOT, "out", "illusion_after.png"))
    else:
        print(render_illusion(iset, sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "out", "illusion.mp4")))
