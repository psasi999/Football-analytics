"""Data helpers: competitions, matches, events (events are cached to data/)."""
import warnings
from pathlib import Path

import pandas as pd
from statsbombpy import sb

warnings.filterwarnings("ignore")  # hides the harmless "no credentials" warning

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)


TEAM_COLORS = ["#4a9be0", "#e8505b"]  # first / second team in the match
CMAPS = ["Blues", "Reds"]


def team_index(events: pd.DataFrame, team: str) -> int:
    """0 for the team listed first in the match, 1 for the other (keeps colours consistent)."""
    return list(events.team.unique()).index(team)


def get_lineups(match_id: int) -> dict:
    """Lineups of one match (team -> DataFrame), cached like events."""
    cache = DATA_DIR / f"lineups_{match_id}.pkl"
    if cache.exists():
        return pd.read_pickle(cache)
    lineups = sb.lineups(match_id=match_id)
    pd.to_pickle(lineups, cache)
    return lineups


def get_competitions() -> pd.DataFrame:
    """All competition/season pairs available in the free open data."""
    return sb.competitions()


def get_matches(competition_id: int, season_id: int) -> pd.DataFrame:
    """All matches of one competition season."""
    return sb.matches(competition_id=competition_id, season_id=season_id)


def get_events(match_id: int) -> pd.DataFrame:
    """Every event of one match. First call downloads, later calls read the cache."""
    cache = DATA_DIR / f"events_{match_id}.pkl"  # pickle keeps list columns (e.g. location) intact
    if cache.exists():
        return pd.read_pickle(cache)
    events = sb.events(match_id=match_id)
    events.to_pickle(cache)
    return events
