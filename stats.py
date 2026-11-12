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


def auth_info(ig_id):
    """Diagnose ohne Token-Inhalt: Token-Art, API-Host, erteilte Rechte, Konto-Insights."""
    info = {"token_type": "instagram-login" if igapi.is_instagram_token() else "facebook-login",
            "host": igapi.base_url(), "checked": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%MZ")}
    if not igapi.is_instagram_token():
        try:
            perms = get("me/permissions").get("data", [])
            info["granted"] = sorted(p["permission"] for p in perms if p.get("status") == "granted")
        except Exception as e:
            info["permissions_error"] = str(e)[:120]
    try:
        get(f"{ig_id}/insights", metric="reach", period="day")
        info["account_insights"] = "ok"
    except Exception as e:
        info["account_insights"] = str(e)[:120]
    return info


def main():
    path = os.path.join(ROOT, "data", "stats.json")
    stats = {"history": []}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            stats = json.load(f)
    ig_id = igapi.ig_user_id()
    stats["auth"] = auth_info(ig_id)
    me = get(ig_id, fields="username,followers_count,media_count")
    media = get(f"{ig_id}/media", fields="id,caption,timestamp,like_count,comments_count,permalink", limit=50).get("data", [])
    for m in media:
        m.pop("caption", None)
        try:
            try:  # Wiedergabedauer zeigt, ob Leute bis zur Aufloesung dranbleiben
                ins = get(f"{m['id']}/insights", metric="views,reach,shares,saved,ig_reels_avg_watch_time")
            except Exception:
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
