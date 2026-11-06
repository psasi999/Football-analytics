"""Step 4: pressing and ball recoveries. Run: python src/pressure_map.py
Question: how high up the pitch did each team win the ball back or press?"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from mplsoccer import Pitch

from load import CMAPS, get_events, team_index

MATCH_ID = 3869685  # Argentina 3-3 France, 2022 final
OUT = Path(__file__).resolve().parent.parent / "outputs" / "pressure_map.png"


def build_fig(events, teams):
    events = events[events.period < 5]  # normal + extra time, no shootout
    d = events[events.type.isin(["Ball Recovery", "Interception", "Pressure"])].copy()
    # A "Ball Recovery" flagged as failed is not a real regain, so drop it
    if "ball_recovery_recovery_failure" in d:
        d = d[d.ball_recovery_recovery_failure != True]  # noqa: E712 (NaN must stay)
    d = d[d.location.notna()]
    d["x"] = d.location.str[0]
    d["y"] = d.location.str[1]

    pitch = Pitch(pitch_type="statsbomb", pitch_color="#22312b", line_color="#c7d5cc")
    fig, axes = pitch.draw(nrows=1, ncols=len(teams), figsize=(8 * len(teams), 6.5))
    fig.set_facecolor("#22312b")

    for ax, team in zip(np.atleast_1d(axes).ravel(), teams):
        t = d[d.team == team]
        # Count events in a 6 x 4 grid of pitch zones, then colour each zone by count
        stat = pitch.bin_statistic(t.x, t.y, bins=(6, 4), statistic="count")
        pitch.heatmap(stat, ax=ax, cmap=CMAPS[team_index(events, team)], edgecolors="#22312b", alpha=0.9)
        ax.axvline(t.x.mean(), color="white", ls="--", lw=1.5)  # average height of the team's defensive actions
        n = t.type.value_counts()
        ax.set_title(f"{team}: avg height {t.x.mean():.0f} / 120\n"
                     f"{n.get('Pressure', 0)} pressures, {n.get('Ball Recovery', 0)} recoveries, "
                     f"{n.get('Interception', 0)} interceptions", color="white", fontsize=13)

    fig.suptitle("Where each team pressed and won the ball back (darker = more actions). "
                 "Teams attack left to right; dashed line = average height.",
                 color="white", fontsize=11, y=1.04)
    return fig


if __name__ == "__main__":
    events = get_events(MATCH_ID)
    fig = build_fig(events, list(events.team.unique()))
    OUT.parent.mkdir(exist_ok=True)
    fig.savefig(OUT, dpi=120, facecolor=fig.get_facecolor(), bbox_inches="tight")
    print(f"Saved {OUT}")
