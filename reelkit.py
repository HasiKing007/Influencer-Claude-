"""Gemeinsame Bausteine fuer die Formate ab 17.11. (facts, odd, rank).

- frames -> MP4 ueber ffmpeg-Pipe
- Tonspur aus numpy-Samples (eigene Synth-Toene, keine fremde Musik)
- optionale KI-Stimme (edge-tts, frei nutzbare Neural-Stimmen). Faellt die Stimme aus,
  wird das Reel ohne Stimme gerendert, damit nie ein Post ausfaellt.
"""
import os
import shutil
import subprocess
import tempfile

import numpy as np
from PIL import Image, ImageDraw

import render as r

RATE = 44100
VOICE = os.environ.get("REEL_VOICE", "en-US-AndrewNeural")
_VOICE_BROKEN = False   # nach dem ersten Fehler im selben Lauf nicht weiter probieren


def gradient(top, bottom):
    k = np.linspace(0, 1, r.H)[:, None]
    col = np.array(top)[None, :] + (np.array(bottom) - np.array(top))[None, :] * k
    arr = np.repeat(col[:, None, :], r.W, axis=1).astype(np.uint8)
    return Image.fromarray(arr, "RGB")


def center_text(d, y, text, path, size, fill, max_width=None):
    max_width = max_width or (r.SAFE_RIGHT - r.SAFE_LEFT)
    f = r.fit_font(d, text, path, size, max_width)
    d.text(((r.SAFE_LEFT + r.SAFE_RIGHT) / 2, y), text, font=f, fill=fill, anchor="mm")
    return f


def wrap(d, text, path, size, max_width, max_lines=3, min_size=34):
    """Bricht Text in Zeilen um; verkleinert die Schrift, bis er in max_lines passt."""
    while True:
        f = r.font(path, size)
        lines, cur = [], ""
        for word in text.split():
            test = (cur + " " + word).strip()
            if d.textlength(test, font=f) <= max_width:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        if len(lines) <= max_lines or size <= min_size:
            return f, lines
        size -= 2


def pill(d, y, text, fill, text_fill, size=50, h=90):
    d.rounded_rectangle((r.SAFE_LEFT, y - h / 2, r.SAFE_RIGHT, y + h / 2), radius=h / 2, fill=fill)
    center_text(d, y, text, r.BOLD, size, text_fill, r.SAFE_RIGHT - r.SAFE_LEFT - 60)


# ---------- Ton ----------

def silence(seconds):
    return np.zeros(int(seconds * RATE) + 1, dtype=np.float64)


def add_tone(buf, start, freq, length, volume=0.3):
    s0 = int(start * RATE)
    n = min(int(length * RATE), len(buf) - s0)
    if n <= 0:
        return
    t = np.arange(n) / RATE
    env = np.exp(-t / (length * 0.35))
    buf[s0:s0 + n] += volume * env * np.sin(2 * np.pi * freq * t)


def add_tick(buf, start, volume=0.25):
    s0 = int(start * RATE)
    n = min(int(0.03 * RATE), len(buf) - s0)
    if n <= 0:
        return
    t = np.arange(n) / RATE
    noise = np.random.default_rng(int(start * 1000)).uniform(-1, 1, n)
    buf[s0:s0 + n] += volume * noise * np.exp(-t / 0.006)


def add_pulse(buf, bpm=118, volume=0.12, start=0.0, end=None):
    """Dezenter Beat (Kick auf jede Viertel), damit das Reel nicht stumm wirkt."""
    end = end or len(buf) / RATE
    beat = 60.0 / bpm
    t0 = start
    while t0 < end:
        s0 = int(t0 * RATE)
        n = min(int(0.18 * RATE), len(buf) - s0)
        if n > 0:
            t = np.arange(n) / RATE
            freq = 110 * np.exp(-t * 18) + 45
            buf[s0:s0 + n] += volume * np.exp(-t / 0.07) * np.sin(2 * np.pi * np.cumsum(freq) / RATE)
        t0 += beat


def voice(text):
    """Sprachclip als numpy-Array (mono, 44,1 kHz) oder None, wenn die Stimme nicht verfuegbar ist."""
    global _VOICE_BROKEN
    if _VOICE_BROKEN or os.environ.get("REEL_NO_VOICE") == "1" or not shutil.which("edge-tts"):
        return None
    tmp = tempfile.mkdtemp()
    mp3, raw = os.path.join(tmp, "v.mp3"), os.path.join(tmp, "v.raw")
    try:
        for attempt in range(2):   # ein Wiederholversuch (Dienst bricht gelegentlich ab)
            try:
                subprocess.run(["edge-tts", "--voice", VOICE, "--rate", "+20%", "--text", text, "--write-media", mp3],
                               check=True, capture_output=True, timeout=25)
                break
            except subprocess.SubprocessError:
                if attempt:
                    raise
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp3, "-f", "s16le", "-ac", "1",
                        "-ar", str(RATE), raw], check=True, timeout=45)
        data = np.fromfile(raw, dtype="<i2").astype(np.float64) / 32768.0
        return data if len(data) > RATE * 0.2 else None
    except Exception as e:  # noqa: BLE001 - Stimme ist optional
        _VOICE_BROKEN = True
        print("Stimme nicht verfuegbar:", str(e)[:200])
        return None
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def clip_len(clip):
    return 0.0 if clip is None else len(clip) / RATE


def add_clip(buf, start, clip, volume=1.0):
    if clip is None:
        return
    s0 = int(start * RATE)
    n = min(len(clip), len(buf) - s0)
    if n > 0:
        buf[s0:s0 + n] += volume * clip[:n]


# ---------- Ausgabe ----------

def encode(out_path, total, frame_fn, audio):
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    silent, wav = out_path + ".silent.mp4", out_path + ".wav"
    enc = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{r.W}x{r.H}", "-r", str(r.FPS), "-i", "-",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
         "-movflags", "+faststart", silent], stdin=subprocess.PIPE)
    for k in range(int(total * r.FPS)):
        enc.stdin.write(frame_fn(k / r.FPS).tobytes())
    enc.stdin.close()
    if enc.wait() != 0:
        raise RuntimeError("ffmpeg (Video) fehlgeschlagen")
    peak = max(1.0, float(np.max(np.abs(audio))) / 0.95)
    pcm = (audio / peak * 32767).astype("<i2")
    import wave
    with wave.open(wav, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(pcm.tobytes())
    tmp = out_path + ".tmp.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", wav,
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
                    "-ar", "44100", "-shortest", "-movflags", "+faststart", tmp], check=True)
    os.replace(tmp, out_path)
    os.remove(silent)
    os.remove(wav)


def draw(img):
    return ImageDraw.Draw(img)
