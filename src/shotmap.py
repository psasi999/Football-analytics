"""Step 1: shot map for one match. Run: python src/shotmap.py
Question: which team created the better chances?"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from mplsoccer import Pitch

from load import TEAM_COLORS, get_events, team_index

MATCH_ID = 3869685  # Argentina 3-3 France, 2022 final
OUT = Path(__file__).resolve().parent.parent / "outputs" / "shotmap.png"


def build_fig(events, teams, title):
    """One half-pitch panel per team in `teams`; marker size = xG, football icon = goal."""
    # Penalty shootout shots are period 5; leave them out so xG reflects play in the match
    shots = events[(events.type == "Shot") & (events.period < 5)].copy()
    shots["x"] = shots.location.str[0]
    shots["y"] = shots.location.str[1]

    pitch = Pitch(pitch_type="statsbomb", half=True, pitch_color="#22312b", line_color="#c7d5cc")
    fig, axes = pitch.draw(nrows=1, ncols=len(teams), figsize=(7 * len(teams), 7))
    for ax, team in zip(np.atleast_1d(axes).ravel(), teams):
        color = TEAM_COLORS[team_index(events, team)]
        t = shots[shots.team == team]
        goals = t[t.shot_outcome == "Goal"]
        misses = t[t.shot_outcome != "Goal"]
        # marker area scales with xG (x 1500 so tiny chances are still visible)
        pitch.scatter(misses.x, misses.y, s=misses.shot_statsbomb_xg * 1500 + 30, ax=ax,
                      color=color, alpha=0.45, edgecolors="white", linewidth=1)
        pitch.scatter(goals.x, goals.y, s=goals.shot_statsbomb_xg * 1500 + 30, ax=ax,
                      marker="football", zorder=5)
        ax.set_title(f"{team}\n{len(t)} shots | {len(goals)} goals | {t.shot_statsbomb_xg.sum():.2f} xG",
                     color="white", fontsize=14)
    fig.set_facecolor("#22312b")
    fig.suptitle(f"{title}\nMarker size = xG (chance quality). Football icon = goal.",
                 color="white", fontsize=15)
    return fig


if __name__ == "__main__":
    events = get_events(MATCH_ID)
    fig = build_fig(events, list(events.team.unique()), "Argentina 3-3 France (2022 World Cup final, incl. extra time)")
    OUT.parent.mkdir(exist_ok=True)
    fig.savefig(OUT, dpi=130, facecolor=fig.get_facecolor())
    print(f"Saved {OUT}")
