"""Step 1b: animated shot map. Run: python src/shotmap_animated.py
Shots appear one by one in match order; press Play or drag the slider."""
from pathlib import Path

import plotly.graph_objects as go

from load import get_events

MATCH_ID = 3869685  # Argentina 3-3 France, 2022 final
OUT = Path(__file__).resolve().parent.parent / "outputs" / "shotmap_animated.html"

events = get_events(MATCH_ID)
shots = events[(events.type == "Shot") & (events.period < 5)].copy()  # no shootout
shots = shots.sort_values(["period", "minute", "second"]).reset_index(drop=True)
teams = list(shots.team.unique())  # first team attacks right, second is flipped to attack left

# One full pitch: flip the second team's coordinates so it attacks the left goal
x = shots.location.str[0]
y = shots.location.str[1]
flip = shots.team == teams[1]
shots["x"] = x.where(~flip, 120 - x)
shots["y"] = y.where(~flip, 80 - y)
shots["is_goal"] = shots.shot_outcome == "Goal"
shots["hover"] = (shots.minute.astype(str) + "' " + shots.player + " (" + shots.team + ")<br>"
                  + shots.shot_type + " | " + shots.shot_outcome
                  + "<br>xG " + shots.shot_statsbomb_xg.round(2).astype(str))
colors = {teams[0]: "#6cb4ee", teams[1]: "#e8505b"}


def traces(upto, grow=1.0):
    """Scatter traces for shots 0..upto (one per team so the legend shows both).
    grow < 1 draws the newest shot smaller and fainter, which gives the fade-in."""
    out = []
    shown = shots.iloc[: upto + 1]
    for team in teams:
        t = shown[shown.team == team]
        g = [grow if i == upto else 1.0 for i in t.index]  # only the newest shot grows
        out.append(go.Scatter(
            x=t.x, y=t.y, mode="markers", name=team, text=t.hover, hoverinfo="text",
            marker=dict(size=(t.shot_statsbomb_xg * 60 + 8) * g, color=colors[team],
                        opacity=[0.6 * k for k in g],
                        symbol=["star" if g else "circle" for g in t.is_goal],
                        line=dict(color="white", width=[3 if g else 1 for g in t.is_goal]))))
    return out


GROW_STEPS = (0.25, 0.6, 1.0)  # 3 frames per shot: small -> medium -> full size
frames = [go.Frame(data=traces(i, g), name=f"{i}_{k}")
          for i in range(len(shots)) for k, g in enumerate(GROW_STEPS)]

# Pitch lines as shapes (StatsBomb 120x80; y axis reversed so it matches the data)
line = dict(color="#c7d5cc", width=2)
rects = [(0, 0, 120, 80), (60, 0, 60, 80), (0, 18, 18, 62), (102, 18, 120, 62),
         (0, 30, 6, 50), (114, 30, 120, 50)]
shapes = [dict(type="rect", x0=a, y0=b, x1=c, y1=d, line=line) for a, b, c, d in rects]
shapes.append(dict(type="circle", x0=50, y0=30, x1=70, y1=50, line=line))

fig = go.Figure(data=traces(0), frames=frames)
fig.update_layout(
    title=dict(text="Argentina 3-3 France, 2022 final<br><sup>Shots in match order. Size = xG, star = goal</sup>",
               font=dict(size=16)),
    legend=dict(orientation="h", y=1.0, x=1, xanchor="right"),
    margin=dict(t=90, b=90, l=10, r=10),
    shapes=shapes, plot_bgcolor="#22312b", paper_bgcolor="#22312b", font_color="white",
    xaxis=dict(range=[-2, 122], visible=False),
    yaxis=dict(range=[82, -2], visible=False, scaleanchor="x"),  # reversed y, equal aspect
    height=600, autosize=True,
    updatemenus=[dict(type="buttons", x=0, y=-0.02, bgcolor="#3d5c4e", showactive=False, font=dict(color="white"), buttons=[
        dict(label="Play", method="animate", args=[None, dict(frame=dict(duration=300), fromcurrent=True)]),
        dict(label="Pause", method="animate", args=[[None], dict(frame=dict(duration=0), mode="immediate")])])],
    sliders=[dict(currentvalue=dict(prefix="Shot "), steps=[
        dict(label=f"{r.minute}'", method="animate", args=[[f"{i}_{len(GROW_STEPS) - 1}"], dict(frame=dict(duration=0), mode="immediate")])
        for i, r in shots.iterrows()])],
)
OUT.parent.mkdir(exist_ok=True)
fig.write_html(OUT)
print(f"Saved {OUT}")
print(shots[shots.is_goal][["minute", "team", "player", "shot_type"]].to_string(index=False))
