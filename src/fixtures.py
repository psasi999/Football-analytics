"""Step 6: current fixtures and standings from football-data.org (free tier).
Setup: get a free key at https://www.football-data.org/client/register, then
    export FOOTBALL_DATA_API_KEY=your_key
Run: python src/fixtures.py [competition code, default PL]"""
import json
import os
import sys
import time
from datetime import date, timedelta

import pandas as pd
import requests

from load import DATA_DIR

BASE = "https://api.football-data.org/v4"
CACHE_SECONDS = 600  # free tier allows 10 requests/minute; cached answers are reused for 10 minutes
# Competitions available on the free tier
COMPETITIONS = {"Premier League": "PL", "La Liga": "PD", "Bundesliga": "BL1", "Serie A": "SA",
                "Ligue 1": "FL1", "Champions League": "CL", "Eredivisie": "DED", "Primeira Liga": "PPL"}


def _get(path: str, params: dict | None = None) -> dict:
    """GET one API path, with a small JSON file cache in data/."""
    key = os.environ.get("FOOTBALL_DATA_API_KEY")
    if not key:
        raise RuntimeError("FOOTBALL_DATA_API_KEY is not set (see the top of src/fixtures.py).")
    name = (path + json.dumps(params or {}, sort_keys=True)).replace("/", "_").replace(" ", "")
    cache = DATA_DIR / f"fd_{name}.json"
    if cache.exists() and time.time() - cache.stat().st_mtime < CACHE_SECONDS:
        return json.loads(cache.read_text())
    r = requests.get(BASE + path, params=params, headers={"X-Auth-Token": key}, timeout=15)
    if r.status_code == 429:
        raise RuntimeError("Rate limit hit (10 requests/minute on the free tier). Wait a minute and retry.")
    if r.status_code == 403:
        raise RuntimeError("Not allowed: that competition is not included in the free tier, or the key is wrong.")
    r.raise_for_status()
    cache.write_text(r.text)
    return r.json()


def get_fixtures(code: str, days: int = 14) -> pd.DataFrame:
    """Matches from 3 days ago to `days` days ahead (recent results + upcoming games)."""
    today = date.today()
    data = _get(f"/competitions/{code}/matches",
                {"dateFrom": (today - timedelta(days=3)).isoformat(), "dateTo": (today + timedelta(days=days)).isoformat()})
    rows = [{"Kick-off (UTC)": m["utcDate"].replace("T", " ")[:16], "Home": m["homeTeam"]["name"],
             "Score": "-" if m["score"]["fullTime"]["home"] is None
             else f'{m["score"]["fullTime"]["home"]}-{m["score"]["fullTime"]["away"]}',
             "Away": m["awayTeam"]["name"], "Status": m["status"]} for m in data["matches"]]
    return pd.DataFrame(rows)


def get_standings(code: str) -> pd.DataFrame:
    """Current league table (TOTAL standings)."""
    data = _get(f"/competitions/{code}/standings")
    table = next(s["table"] for s in data["standings"] if s["type"] == "TOTAL")
    return pd.DataFrame([{"Pos": t["position"], "Team": t["team"]["name"], "P": t["playedGames"], "W": t["won"],
                          "D": t["draw"], "L": t["lost"], "GF": t["goalsFor"], "GA": t["goalsAgainst"],
                          "GD": t["goalDifference"], "Pts": t["points"]} for t in table])


if __name__ == "__main__":
    code = sys.argv[1] if len(sys.argv) > 1 else "PL"
    try:
        print(get_standings(code).to_string(index=False))
        print()
        print(get_fixtures(code).to_string(index=False))
    except RuntimeError as e:
        print(f"Failed: {e}")
