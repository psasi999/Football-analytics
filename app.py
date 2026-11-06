"""Step 5: Streamlit dashboard. Run: streamlit run app.py"""
import sys
import warnings

import matplotlib.pyplot as plt
import streamlit as st

sys.path.insert(0, "src")  # so we can import the chart modules from src/
import pass_network
import pressure_map
import shotmap
import xg_timeline
from fixtures import COMPETITIONS, get_fixtures, get_standings
from load import get_competitions, get_events, get_matches

warnings.filterwarnings("ignore")
st.set_page_config(page_title="Football analytics", layout="wide")


# Cache data calls so changing a widget does not re-download anything
@st.cache_data
def competitions():
    return get_competitions()


@st.cache_data
def matches(comp_id, season_id):
    return get_matches(comp_id, season_id)


@st.cache_data
def events(match_id):
    return get_events(match_id)


def show(fig):
    st.pyplot(fig)
    plt.close(fig)  # free memory; Streamlit reruns the script on every click


# ---- Sidebar: competition -> season -> match -> team ----
st.sidebar.title("Pick a match")
comps = competitions()
comp = st.sidebar.selectbox("Competition", sorted(comps.competition_name.unique()))
seasons = comps[comps.competition_name == comp].sort_values("season_name", ascending=False)
season = st.sidebar.selectbox("Season", seasons.season_name)
row = seasons[seasons.season_name == season].iloc[0]

ms = matches(row.competition_id, row.season_id).sort_values("match_date")
labels = {f"{m.match_date}  {m.home_team} {m.home_score}-{m.away_score} {m.away_team}": m for m in ms.itertuples()}
match = labels[st.sidebar.selectbox("Match", list(labels))]
team = st.sidebar.selectbox("Team (for pass network and pressing)", [match.home_team, match.away_team])

title = f"{match.home_team} {match.home_score}-{match.away_score} {match.away_team} ({comp} {season})"
ev = events(match.match_id)
both = list(ev.team.unique())

st.title(title)
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Shot map", "xG timeline", "Pass network", "Pressing", "Fixtures (current)"])

with tab1:
    st.caption("Who created the better chances? Bigger circle = higher xG (chance of scoring). Both teams shown.")
    show(shotmap.build_fig(ev, both, title))
with tab2:
    st.caption("Who was creating danger at each moment? Steps up = a shot; big dot = goal. Both teams shown.")
    show(xg_timeline.build_fig(ev, title))
with tab3:
    st.caption(f"How was {team} structured? Dots = average passing positions, lines = pass counts. "
               "Starting XI until the first substitution.")
    show(pass_network.build_fig(ev, match.match_id, [team]))
with tab4:
    st.caption(f"Where did {team} press and win the ball back? Darker = more pressures, recoveries, interceptions.")
    show(pressure_map.build_fig(ev, [team]))
with tab5:
    # Live data (football-data.org): independent of the historical match chosen in the sidebar
    st.caption("Current league table and fixtures from football-data.org (free tier). "
               "Open data above is historical only; this tab is today's football.")
    league = st.selectbox("League", list(COMPETITIONS))

    @st.cache_data(ttl=600)
    def live(code):
        return get_standings(code), get_fixtures(code)

    try:
        table, fixtures = live(COMPETITIONS[league])
        st.subheader("Standings")
        st.dataframe(table, hide_index=True, use_container_width=True)
        st.subheader("Recent and upcoming fixtures")
        st.dataframe(fixtures, hide_index=True, use_container_width=True)
    except RuntimeError as e:
        st.info(str(e))
    except Exception as e:  # network down, API change, etc.
        st.error(f"Could not load live data: {e}")
