#!/usr/bin/env python3
"""
One-time interactive Strava OAuth bootstrap.

Stores client_id, client_secret and a long-lived refresh_token in the macOS
keyring (service "fabriziogf-strava") so the daily updater can run unattended.

Prereq — register an API application at https://www.strava.com/settings/api
  - Authorization Callback Domain: localhost
You'll get a Client ID and Client Secret on that page.

Run:
  /Users/fabriziogiovanninifilho/ai-projects/trainingpeaks-mcp/.venv/bin/python3 \
      scripts/strava_auth.py
"""

from __future__ import annotations

import json
import urllib.parse
import urllib.request

import keyring

SERVICE = "fabriziogf-strava"
REDIRECT = "http://localhost/exchange_token"
SCOPE = "activity:read_all"


def _post(url: str, data: dict) -> dict:
    body = urllib.parse.urlencode(data).encode()
    with urllib.request.urlopen(urllib.request.Request(url, data=body), timeout=30) as r:
        return json.loads(r.read().decode())


def main() -> None:
    client_id = input("Strava Client ID: ").strip()
    client_secret = input("Strava Client Secret: ").strip()

    auth_url = "https://www.strava.com/oauth/authorize?" + urllib.parse.urlencode({
        "client_id": client_id,
        "redirect_uri": REDIRECT,
        "response_type": "code",
        "approval_prompt": "force",
        "scope": SCOPE,
    })

    print("\n1. Open this URL in your browser and click Authorize:\n")
    print("   " + auth_url + "\n")
    print("2. Your browser will redirect to a localhost URL that fails to load")
    print("   (that's expected). Copy the FULL address bar URL — it contains")
    print("   ...&code=XXXXX&...\n")

    redirected = input("Paste the full redirected URL (or just the code): ").strip()
    if "code=" in redirected:
        code = urllib.parse.parse_qs(urllib.parse.urlparse(redirected).query)["code"][0]
    else:
        code = redirected

    print("\nExchanging code for tokens…")
    tok = _post("https://www.strava.com/oauth/token", {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code",
    })

    if "refresh_token" not in tok:
        print("ERROR: no refresh_token in response:")
        print(json.dumps(tok, indent=2))
        return

    keyring.set_password(SERVICE, "client_id", client_id)
    keyring.set_password(SERVICE, "client_secret", client_secret)
    keyring.set_password(SERVICE, "refresh_token", tok["refresh_token"])

    athlete = tok.get("athlete", {})
    print("\n✅ Stored credentials in keyring service 'fabriziogf-strava'.")
    print(f"   Authorized as: {athlete.get('firstname','')} {athlete.get('lastname','')} "
          f"(athlete {athlete.get('id','?')})")
    print(f"   Granted scope: {SCOPE}")
    print("\nTest it:  python3 scripts/strava_client.py")


if __name__ == "__main__":
    main()
