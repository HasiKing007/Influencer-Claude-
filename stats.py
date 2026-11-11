"""Schreibt Kennzahlen des Accounts nach data/stats.json (Grundlage fuer die woechentliche Auswertung).

Schlaegt nie mit Fehlercode fehl, damit das Posten davon unabhaengig bleibt.
"""
import datetime
import json
import os

import igapi

ROOT = os.path.dirname(os.path.abspath(__file__))


def get(path, **params):
    return igapi.call("GET", path, **params)


def main():
    path = os.path.join(ROOT, "data", "stats.json")
    stats = {"history": []}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            stats = json.load(f)
    ig_id = igapi.ig_user_id()
    me = get(ig_id, fields="username,followers_count,media_count")
    media = get(f"{ig_id}/media", fields="id,caption,timestamp,like_count,comments_count,permalink", limit=50).get("data", [])
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
