"""Step 2: cumulative xG timeline. Run: python src/xg_timeline.py
Question: who was creating the better chances at each point of the match?"""
from pathlib import Path

import matplotlib.pyplot as plt

from load import TEAM_COLORS, get_events, team_index

MATCH_ID = 3869685  # Argentina 3-3 France, 2022 final
OUT = Path(__file__).resolve().parent.parent / "outputs" / "xg_timeline.png"


def short_name(full):
    """Surname for labels. shortcut: 'Di María' is special-cased, other multi-part surnames may be off."""
    if "Di María" in full:
        return "Di María"
    parts = full.split()
    return parts[-2] if len(parts) > 2 else parts[-1]


def build_fig(events, title):
    events = events[events.period < 5]  # no shootout
    shots = events[events.type == "Shot"].copy()
    # StatsBomb minutes keep counting through extra time, so use them directly
    shots["t"] = shots.minute + shots.second / 60
    end = events.minute.max()

    fig, ax = plt.subplots(figsize=(12, 6))
    for team, t in shots.sort_values("t").groupby("team"):
        color = TEAM_COLORS[team_index(events, team)]
        cum = t.shot_statsbomb_xg.cumsum()
        # step line: xG only jumps at the moment of a shot; start at 0 and run to the final whistle
        ax.step([0, *t.t, end], [0, *cum, cum.iloc[-1]], where="post", lw=2.5,
                color=color, label=f"{team} ({cum.iloc[-1]:.2f} xG)")
        goals = t[t.shot_outcome == "Goal"]
        ax.scatter(goals.t, cum[goals.index], s=160, color=color, edgecolor="black", zorder=5)
        for _, g in goals.iterrows():  # label each goal with scorer surname and minute
            ax.annotate(f"{short_name(g.player)} {g.minute}'", (g.t, cum[g.name]),
                        textcoords="offset points", xytext=(-8, 12), fontsize=9, ha="right", color=color)

    # Half / extra-time boundaries (only those the match reached)
    for m, label in [(45, "HT"), (90, "FT"), (105, "ET HT")]:
        if m <= end:
            ax.axvline(m, color="grey", ls="--", lw=1)
            ax.text(m, ax.get_ylim()[1], label, ha="center", va="bottom", fontsize=9, color="grey")

    ax.set_xlabel("Match minute")
    ax.set_ylabel("Cumulative xG")
    ax.set_title(f"{title}: cumulative xG (big dots = goals)", pad=22)
    ax.legend(loc="upper left")
    ax.grid(alpha=0.3)
    return fig


if __name__ == "__main__":
    fig = build_fig(get_events(MATCH_ID), "Argentina 3-3 France, 2022 final")
    OUT.parent.mkdir(exist_ok=True)
    fig.savefig(OUT, dpi=130, bbox_inches="tight")
    print(f"Saved {OUT}")
