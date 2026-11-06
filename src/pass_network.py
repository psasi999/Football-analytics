"""Step 3: pass network. Run: python src/pass_network.py
Question: how was each team structured while its starting XI was still on the pitch?"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from mplsoccer import Pitch

from load import TEAM_COLORS, get_events, get_lineups, team_index

MATCH_ID = 3869685  # Argentina 3-3 France, 2022 final
OUT = Path(__file__).resolve().parent.parent / "outputs" / "pass_network.png"
MIN_PASSES = 3  # hide links with fewer passes so the picture stays readable


def build_fig(events, match_id, teams):
    events = events[events.period < 5].copy()
    events["t"] = events.minute * 60 + events.second  # seconds since kick-off

    # Short display names (nickname's last word) from the lineups
    short = {}
    for lineup in get_lineups(match_id).values():
        for _, p in lineup.iterrows():
            name = p.player_name if pd.isna(p.player_nickname) else p.player_nickname
            short[p.player_name] = name.split()[-1]

    pitch = Pitch(pitch_type="statsbomb", pitch_color="#22312b", line_color="#c7d5cc")
    fig, axes = pitch.draw(nrows=1, ncols=len(teams), figsize=(8 * len(teams), 6.5))
    fig.set_facecolor("#22312b")

    for ax, team in zip(np.atleast_1d(axes).ravel(), teams):
        color = TEAM_COLORS[team_index(events, team)]
        # Window = kick-off until this team's first substitution (whole match if it made none)
        subs = events[(events.team == team) & (events.type == "Substitution")].t
        first_sub = subs.min() if len(subs) else events.t.max() + 1
        # Completed passes only: pass_outcome is empty when the pass succeeded
        p = events[(events.team == team) & (events.type == "Pass") & (events.t < first_sub)
                   & events.pass_outcome.isna() & events.pass_recipient.notna()].copy()
        p["x"] = p.location.str[0]
        p["y"] = p.location.str[1]

        # Node = average pass origin per player; size = number of passes made
        nodes = p.groupby("player").agg(x=("x", "mean"), y=("y", "mean"), n=("id", "count"))
        # Link = passes between two players (A->B and B->A merged into one link)
        pair = p.assign(a=p[["player", "pass_recipient"]].min(axis=1), b=p[["player", "pass_recipient"]].max(axis=1))
        links = pair.groupby(["a", "b"]).size().reset_index(name="count")
        links = links[(links["count"] >= MIN_PASSES) & links.a.isin(nodes.index) & links.b.isin(nodes.index)]

        for _, l in links.iterrows():
            pitch.lines(nodes.x[l.a], nodes.y[l.a], nodes.x[l.b], nodes.y[l.b], ax=ax,
                        lw=l["count"] * 0.7, color=color, alpha=0.55, zorder=2)
        pitch.scatter(nodes.x, nodes.y, s=nodes.n * 12 + 80, ax=ax, color=color,
                      edgecolors="white", linewidth=1.5, zorder=3)
        for name, r in nodes.iterrows():
            ax.text(r.x, r.y + 4.5, short.get(name, name), ha="center", va="center",
                    color="white", fontsize=9, zorder=4)
        window = f"until first substitution ({int(first_sub // 60)}')" if len(subs) else "whole match, no substitutions"
        ax.set_title(f"{team}: starting XI {window}\n{len(p)} completed passes", color="white", fontsize=13)

    fig.suptitle("Dot = average pass position, size = passes made, "
                 f"line width = passes between two players (min {MIN_PASSES}). Teams attack left to right.",
                 color="white", fontsize=11, y=1.04)
    return fig


if __name__ == "__main__":
    events = get_events(MATCH_ID)
    fig = build_fig(events, MATCH_ID, list(events.team.unique()))
    OUT.parent.mkdir(exist_ok=True)
    fig.savefig(OUT, dpi=120, facecolor=fig.get_facecolor(), bbox_inches="tight")
    print(f"Saved {OUT}")
