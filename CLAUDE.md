# Football Analytics Learning Project

## Goal
Learn how modern football analytics works by building visualizations from StatsBomb Open Data. The point is understanding the football, not just owning a dashboard.

## Rules (follow always)
1. One question per chart. State the football question first (e.g. "Why did team X lose despite more shots?"), then build the chart that answers it.
2. After building each step, explain in plain language: what the data fields mean, what the chart shows, and how to read it. Keep it short.
3. Build one step at a time. Run it, confirm it works, show the output path, then stop and wait for the user before the next step.
4. No ML or prediction models. Out of scope.
5. Do not use unofficial FIFA endpoints (api.fifa.com) or scrape FBref/Transfermarkt. Data sources are only those listed below.
6. If something fails, say what failed and the fix. Do not silently work around it.
7. Keep code simple and commented. Prefer clarity over cleverness.

## Stack
- Python 3.10+
- statsbombpy (data), pandas
- mplsoccer + matplotlib (pitch plots)
- plotly (interactive charts where useful)
- streamlit (final dashboard)

## Setup
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install statsbombpy pandas mplsoccer matplotlib plotly streamlit
```
StatsBomb open data needs no API key. `statsbombpy` may print a credentials warning; ignore it.

## Project structure
```
football/
  CLAUDE.md
  data/            # cached CSVs (optional)
  src/
    load.py        # competitions, matches, events helpers
    shotmap.py
    xg_timeline.py
    pass_network.py
    pressure_map.py
  outputs/         # saved PNGs
  app.py           # Streamlit dashboard (step 5)
```

## Data notes
- StatsBomb open data is a curated set (some World Cups, Euros, selected leagues and seasons), NOT every league or current season. Always list available competitions first with `sb.competitions()` and tell the user what exists.
- Pitch coordinates: 120 x 80, attacking left to right. Use `mplsoccer.Pitch(pitch_type='statsbomb')`.
- Events are in `sb.events(match_id=...)`. Key columns: `type`, `team`, `player`, `location`, `shot_statsbomb_xg`, `shot_outcome`, `pass_end_location`, `minute`.
- Cache events to `data/` to avoid refetching.

## Steps
**Step 0: Explore.** List competitions, pick a World Cup, list its matches, load one match's events, print the event types and counts. Explain the data structure.

**Step 1: Shot map (one match).** Both teams, shots plotted on the pitch, marker size = xG, goals highlighted. Save to `outputs/shotmap.png`. Explain what xG is.

**Step 2: xG timeline.** Cumulative xG per team over match minutes, goals marked. Explain how a team can win while being outplayed (and the reverse).

**Step 3: Pass network.** Average player position (from pass origins) with links sized by pass count between players, for the starting XI until the first substitution. Explain what it reveals about structure.

**Step 4: Pressing and ball recoveries.** Heatmap of where each team wins the ball back (ball recoveries, interceptions, pressure events). Explain what pressing height means tactically.

**Step 5: Streamlit dashboard (`app.py`).** Sidebar: competition -> season -> match -> team. Tabs for each chart above, all driven by the selection. Run with `streamlit run app.py`.

**Step 6 (optional, only if the user asks): current fixtures.** Add football-data.org (free API key, respect rate limits, cache responses) for current fixtures and standings alongside the historical analysis.

## Definition of done per step
- Script runs end to end with one command.
- Output file or app view exists.
- A short plain-language explanation of the football concept was given.
