"""Waehlt das naechste Quiz, rendert das Reel und veroeffentlicht es auf Instagram.

Umgebungsvariablen:
  IG_ACCESS_TOKEN     Instagram-Token (Instagram API with Instagram Login)
  GITHUB_REPOSITORY   "besitzer/repo" (setzt GitHub Actions automatisch)
  DRY_RUN=1           nur rendern, nichts hochladen
"""
import datetime
import json
import os
import subprocess
import sys
import time

import requests

import igapi
import render

ROOT = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(ROOT, "data", "state.json")
QUIZZES = os.path.join(ROOT, "data", "quizzes.json")

CAPTIONS = [
    "Can you guess the player from his career path? Comment your answer before the reveal!",
    "Only real football fans get this one before the countdown ends. Who is it?",
    "How many clubs did you need? Drop the number in the comments.",
    "One career, one player. Did you get it before the reveal?",
    "Send this to the friend who thinks he knows football.",
]
# Instagram erlaubt seit Dez. 2025 nur noch 5 Hashtags pro Reel
TAGS = "#footballquiz #guesstheplayer #football #soccer #footballtrivia"


def load(path, default):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return default


def pick(quizzes, state):
    posted = [p["id"] for p in state["posted"]]
    for q in quizzes:
        if q["id"] not in posted:
            return q
    # Warteschlange leer: das am laengsten zurueckliegende Quiz wiederholen
    oldest = min(quizzes, key=lambda q: max(i for i, p in enumerate(posted) if p == q["id"]))
    print("Warnung: keine neuen Quizze mehr, wiederhole", oldest["id"])
    return oldest


def git(*args, **kw):
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True, cwd=ROOT, **kw).stdout.strip()


def publish_file(path):
    """Legt das Video als einzelnen Commit auf den Branch 'media' und liefert oeffentliche URLs."""
    blob = git("hash-object", "-w", path)
    tree = git("mktree", input=f"100644 blob {blob}\treel.mp4\n")
    commit = git("commit-tree", tree, "-m", "reel")
    git("push", "--force", "origin", f"{commit}:refs/heads/media")
    repo = os.environ["GITHUB_REPOSITORY"]
    return [
        f"https://cdn.jsdelivr.net/gh/{repo}@{commit}/reel.mp4",
        f"https://raw.githubusercontent.com/{repo}/{commit}/reel.mp4",
    ]


def reachable(url, tries=12):
    for _ in range(tries):
        try:
            if requests.head(url, allow_redirects=True, timeout=20).status_code == 200:
                return True
        except requests.RequestException:
            pass
        time.sleep(10)
    return False


api = igapi.call


def post_reel(urls, caption, thumb_offset_ms=None):
    ig_id = igapi.ig_user_id()
    print("Account:", api("GET", ig_id, fields="username").get("username"))
    last_error = None
    for url in urls:
        if not reachable(url):
            print("Nicht erreichbar:", url)
            continue
        try:
            extra = {"thumb_offset": thumb_offset_ms} if thumb_offset_ms else {}
            try:
                container = api("POST", f"{ig_id}/media", media_type="REELS", video_url=url, caption=caption, **extra)["id"]
            except RuntimeError as e:
                if not extra:
                    raise
                print("Titelbild-Parameter abgelehnt, poste ohne:", e)
                container = api("POST", f"{ig_id}/media", media_type="REELS", video_url=url, caption=caption)["id"]
            for _ in range(20):
                time.sleep(30)
                status = api("GET", container, fields="status_code,status")
                print("Status:", status.get("status_code"))
                if status.get("status_code") == "FINISHED":
                    return api("POST", f"{ig_id}/media_publish", creation_id=container)["id"]
                if status.get("status_code") in ("ERROR", "EXPIRED"):
                    raise RuntimeError(f"Verarbeitung fehlgeschlagen: {status}")
            raise RuntimeError("Zeitueberschreitung bei der Verarbeitung")
        except RuntimeError as e:
            last_error = e
            print("Fehler mit", url, "->", e)
    raise SystemExit(f"Veroeffentlichen fehlgeschlagen: {last_error}")


SLOT_GAP_MIN = 90    # Slots liegen 4 h auseinander; Ersatzlaeufe innerhalb davon posten nicht
MAX_PER_DAY = 4     # Sicherheitsgrenze (Regel: nie mehr als 5)


def already_posted_in_slot(state):
    """Verhindert Doppelposts durch Ersatz-Termine und externe Ausloeser (ausser FORCE=1)."""
    if os.environ.get("FORCE") == "1":
        return False
    now = datetime.datetime.utcnow()
    dates = [datetime.datetime.strptime(p["date"], "%Y-%m-%dT%H:%MZ") for p in state["posted"] if p.get("date")]
    if any((now - d).total_seconds() < SLOT_GAP_MIN * 60 for d in dates):
        print("In diesem Slot wurde schon gepostet, ueberspringe.")
        return True
    if sum(d.date() == now.date() for d in dates) >= MAX_PER_DAY:
        print("Tageslimit erreicht, ueberspringe.")
        return True
    return False


def main():
    quizzes = load(QUIZZES, [])
    state = load(STATE, {"posted": []})
    if already_posted_in_slot(state):
        return
    quiz = pick(quizzes, state)
    out = render.render(quiz, os.path.join(ROOT, "out", "reel.mp4"))
    caption_idx = len(state["posted"]) % len(CAPTIONS)
    caption = CAPTIONS[caption_idx] + "\n\n" + TAGS
    print("Gerendert:", quiz["id"], out)
    if os.environ.get("DRY_RUN") == "1":
        print("DRY_RUN: nichts veroeffentlicht")
        return
    # Titelbild = alle Stationen sichtbar, kurz vor dem Countdown (statt leerem ersten Frame)
    stations_end = render.timing(len(quiz["clubs"]))[1]
    thumb_ms = int((stations_end - 0.05) * 1000)
    media_id = post_reel(publish_file(out), caption, thumb_ms)
    state["posted"].append({"id": quiz["id"], "media_id": media_id, "caption": caption_idx,
                            "date": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%MZ")})
    with open(STATE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    print("Veroeffentlicht, Media-ID:", media_id)


if __name__ == "__main__":
    sys.exit(main())
