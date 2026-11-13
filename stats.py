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


ANSWER_AFTER_H = 2  # Kommentar-Variante: so lange duerfen Zuschauer raten


def post_answers(stats):
    """Postet bei Quiz-Reels ohne Aufloesung die Antwort als Kommentar (einmal pro Reel)."""
    with open(os.path.join(ROOT, "data", "state.json"), encoding="utf-8") as f:
        posted = json.load(f)["posted"]
    with open(os.path.join(ROOT, "data", "quizzes.json"), encoding="utf-8") as f:
        answers = {q["id"]: q["answer"] for q in json.load(f)}
    done = stats.setdefault("answer_comments", {})
    now = datetime.datetime.utcnow()
    for p in posted:
        if p.get("reveal", True) or not p.get("media_id") or p["media_id"] in done or p["id"] not in answers:
            continue
        age_h = (now - datetime.datetime.strptime(p["date"], "%Y-%m-%dT%H:%MZ")).total_seconds() / 3600
        if age_h < ANSWER_AFTER_H:
            continue
        try:
            igapi.call("POST", f"{p['media_id']}/comments",
                       message=f"ANSWER: {answers[p['id']]}! Did you get it? Follow for a new one every day.")
            done[p["media_id"]] = now.strftime("%Y-%m-%dT%H:%MZ")
            print("Antwort-Kommentar gepostet:", p["id"])
        except Exception as e:
            print("Antwort-Kommentar fehlgeschlagen:", p["id"], str(e)[:120])


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
    post_answers(stats)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    print("Follower:", me.get("followers_count"))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Statistik uebersprungen:", e)
