"""Step 0: explore what data exists. Run: python src/step0_explore.py"""
from load import get_competitions, get_matches, get_events

pd_opts = dict(width=200)

# 1) What competitions exist?
comps = get_competitions()
print("=== Available competitions (one row per season) ===")
print(comps[["competition_id", "season_id", "competition_name", "season_name"]]
      .sort_values(["competition_name", "season_name"]).to_string(index=False))

# 2) Pick the men's FIFA World Cup, latest season in the data
wc = comps[comps.competition_name == "FIFA World Cup"].sort_values("season_name").iloc[-1]
print(f"\nChosen: {wc.competition_name} {wc.season_name}")

# 3) List its matches
matches = get_matches(wc.competition_id, wc.season_id)
print(f"\n=== {len(matches)} matches ===")
cols = ["match_id", "match_date", "home_team", "away_team", "home_score", "away_score", "competition_stage"]
print(matches[cols].sort_values("match_date").to_string(index=False))

# 4) Load the final (last match) and count event types
final = matches.sort_values("match_date").iloc[-1]
print(f"\nLoading events for: {final.home_team} {final.home_score}-{final.away_score} {final.away_team}")
events = get_events(final.match_id)
print(f"\n=== {len(events)} events, {events.shape[1]} columns ===")
print(events["type"].value_counts().to_string())

print("\nSample rows:")
print(events[["minute", "team", "player", "type", "location"]].head(8).to_string(index=False))
