#!/usr/bin/env python3
"""
Minimal Strava API client (stdlib only — no `requests` needed).

Credentials live in the macOS keyring under service "fabriziogf-strava",
mirroring how the TrainingPeaks integration stores its secrets:

    client_id      keyring get fabriziogf-strava client_id
    client_secret  keyring get fabriziogf-strava client_secret
    refresh_token  keyring get fabriziogf-strava refresh_token

Run `scripts/strava_auth.py` once to populate them (interactive OAuth).
After that this client refreshes the short-lived access token on every run
and rotates the stored refresh_token automatically.
"""

from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from typing import Any

import keyring

SERVICE = "fabriziogf-strava"
API = "https://www.strava.com/api/v3"
TOKEN_URL = "https://www.strava.com/oauth/token"


# ── keyring helpers ──────────────────────────────────────────────────────────
def kget(key: str) -> str | None:
    return keyring.get_password(SERVICE, key)


def kset(key: str, value: str) -> None:
    keyring.set_password(SERVICE, key, value)


# ── HTTP (stdlib) ────────────────────────────────────────────────────────────
def _http(url: str, *, data: dict | None = None, headers: dict | None = None) -> Any:
    """POST if data is given (form-encoded), else GET. Returns parsed JSON."""
    body = urllib.parse.urlencode(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers or {})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


# ── Sport classifier ─────────────────────────────────────────────────────────
# Strava `sport_type` (preferred) / legacy `type` → dashboard sport bucket.
SPORT_MAP: dict[str, str] = {
    "Swim":            "swim",
    "Ride":            "bike",
    "VirtualRide":     "bike",
    "GravelRide":      "bike",
    "MountainBikeRide": "bike",
    "EBikeRide":       "bike",
    "Run":             "run",
    "TrailRun":        "run",
    "VirtualRun":      "run",
    "Walk":            "run",
    "Hike":            "run",
    "WeightTraining":  "strength",
    "Workout":         "strength",
    "Crossfit":        "strength",
}


def classify(activity: dict) -> str:
    key = activity.get("sport_type") or activity.get("type") or ""
    return SPORT_MAP.get(key, "other")


# ── Client ───────────────────────────────────────────────────────────────────
class StravaClient:
    def __init__(self) -> None:
        self.client_id = kget("client_id")
        self.client_secret = kget("client_secret")
        self.refresh_token = kget("refresh_token")
        if not all([self.client_id, self.client_secret, self.refresh_token]):
            raise RuntimeError(
                "Strava credentials missing from keyring. "
                "Run scripts/strava_auth.py once to set them up."
            )
        self._access_token: str | None = None

    def _ensure_token(self) -> str:
        if self._access_token:
            return self._access_token
        tok = _http(TOKEN_URL, data={
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
        })
        self._access_token = tok["access_token"]
        # Strava rotates the refresh token — persist the new one.
        new_refresh = tok.get("refresh_token")
        if new_refresh and new_refresh != self.refresh_token:
            kset("refresh_token", new_refresh)
            self.refresh_token = new_refresh
        return self._access_token

    def _get(self, path: str, **params) -> Any:
        token = self._ensure_token()
        qs = ("?" + urllib.parse.urlencode(params)) if params else ""
        return _http(API + path + qs, headers={"Authorization": f"Bearer {token}"})

    # ── Endpoints ────────────────────────────────────────────────────────────
    def activities(self, after: int, before: int) -> list[dict]:
        """All activities in [after, before] (epoch seconds), summary objects."""
        out: list[dict] = []
        page = 1
        while True:
            batch = self._get(
                "/athlete/activities",
                after=after, before=before, per_page=200, page=page,
            )
            if not batch:
                break
            out.extend(batch)
            if len(batch) < 200:
                break
            page += 1
        return out

    def activity_detail(self, activity_id: int) -> dict:
        """Detailed activity — includes `best_efforts` for runs."""
        return self._get(f"/activities/{activity_id}", include_all_efforts="true")


if __name__ == "__main__":
    # Smoke test: print the last 30 days of activities.
    import datetime
    c = StravaClient()
    now = int(time.time())
    acts = c.activities(after=now - 30 * 86400, before=now)
    print(f"{len(acts)} activities in last 30 days")
    for a in acts[:15]:
        d = a.get("start_date_local", "")[:10]
        print(f"  {d}  {classify(a):8}  {a.get('sport_type',''):12}  "
              f"{a.get('distance',0)/1000:6.1f} km  {a.get('name','')}")
