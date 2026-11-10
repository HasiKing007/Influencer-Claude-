"""Schreibt Kennzahlen des Accounts nach data/stats.json (Grundlage fuer die woechentliche Auswertung).

Schlaegt nie mit Fehlercode fehl, damit das Posten davon unabhaengig bleibt.
"""
import datetime
import json
import os

import requests

ROOT = os.path.dirname(os.path.abspath(__file__))
API = "https://graph.instagram.com"
TOKEN = os.environ.get("IG_ACCESS_TOKEN", "")


def get(path, **params):
    params["access_token"] = TOKEN
    r = requests.get(f"{API}/{path}", params=params, timeout=60)
    r.raise_for_status()
    return r.json()


def main():
    path = os.path.join(ROOT, "data", "stats.json")
    stats = {"history": []}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            stats = json.load(f)
    me = get("me", fields="username,followers_count,media_count")
    media = get("me/media", fields="id,caption,timestamp,like_count,comments_count,permalink", limit=50).get("data", [])
    for m in media:
        m.pop("caption", None)
        try:
            ins = get(f"{m['id']}/insights", metric="views,reach,shares,saved")
            m["insights"] = {d["name"]: d["values"][0]["value"] for d in ins.get("data", [])}
        except Exception as e:
            m["insights_error"] = str(e)[:120]
    today = datetime.date.today().isoformat()
    stats["history"] = [h for h in stats["history"] if h["date"] != today]
    stats["history"].append({"date": today, "followers": me.get("followers_count"), "posts": me.get("media_count")})
    stats["media"] = media
    with open(path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    print("Follower:", me.get("followers_count"))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Statistik uebersprungen:", e)
