"""Gemeinsamer Zugriff auf die Instagram-Schnittstelle.

Unterstuetzt beide Token-Arten:
  - Instagram-Login-Token (beginnt mit "IG")  -> graph.instagram.com
  - Unified Login / Systemnutzer-Token (SUAT, beginnt mit "EA") -> graph.facebook.com

Optionale Umgebungsvariablen:
  IG_USER_ID       Instagram-Konto-ID, falls die automatische Suche nichts findet
  IG_API_HOST      Host erzwingen, z. B. https://graph.facebook.com
  IG_API_VERSION   z. B. v23.0
"""
import json
import os

import requests

TOKEN = os.environ.get("IG_ACCESS_TOKEN", "").strip()


def is_instagram_token(token=TOKEN):
    return token.startswith("IG")


def base_url():
    host = os.environ.get("IG_API_HOST") or (
        "https://graph.instagram.com" if is_instagram_token() else "https://graph.facebook.com")
    version = os.environ.get("IG_API_VERSION")
    return host.rstrip("/") + ("/" + version if version else "")


def call(method, path, **params):
    params["access_token"] = TOKEN
    r = requests.request(method, f"{base_url()}/{path}", data=params if method == "POST" else None,
                         params=params if method != "POST" else None, timeout=60)
    try:
        body = r.json()
    except ValueError:
        body = {"error": r.text[:300]}
    if r.status_code != 200 or "error" in body:
        raise RuntimeError(f"Instagram API {path}: {json.dumps(body.get('error', body))}")
    return body


def _try(path, **params):
    try:
        return call("GET", path, **params)
    except RuntimeError as e:
        print("Suche:", e)
        return {}


def ig_user_id():
    """Liefert die ID des Instagram-Kontos, auf das gepostet wird."""
    if os.environ.get("IG_USER_ID"):
        return os.environ["IG_USER_ID"].strip()
    if is_instagram_token():
        return call("GET", "me", fields="user_id")["user_id"]
    found = []
    # 1) Instagram-Konten, die ueber eine Facebook-Seite verbunden sind
    for page in _try("me/accounts", fields="instagram_business_account{id,username}").get("data", []):
        if page.get("instagram_business_account"):
            found.append(page["instagram_business_account"])
    # 2) Instagram-Konten im Business-Portfolio (Systemnutzer)
    if not found:
        for biz in _try("me/businesses", fields="id").get("data", []):
            for edge in ("instagram_business_accounts", "owned_instagram_accounts", "instagram_accounts"):
                found += _try(f"{biz['id']}/{edge}", fields="id,username").get("data", [])
                if found:
                    break
    # 3) Assets, die dem Systemnutzer direkt zugewiesen sind
    if not found:
        found += _try("me/assigned_instagram_accounts", fields="id,username").get("data", [])
    if not found:
        raise SystemExit("Kein Instagram-Konto gefunden. Bitte die Konto-ID als Repository-Variable "
                         "IG_USER_ID hinterlegen (Settings > Secrets and variables > Actions > Variables).")
    print("Gefundene Instagram-Konten:", ", ".join(f"{a.get('username')} ({a['id']})" for a in found))
    return found[0]["id"]
