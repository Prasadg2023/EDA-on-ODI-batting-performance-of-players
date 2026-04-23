from pathlib import Path
from typing import Any
from html import escape

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


DATA_PATH = Path(__file__).with_name("Player_stats_Clean_Dataset.csv")

NUMERIC_COLUMNS = [
    "Matches",
    "Innings",
    "Not_Out",
    "Total_Runs",
    "Highest_Score",
    "Batting_Average",
    "Ball_Faced",
    "Strike_Rate",
    "100's",
    "50's",
    "Career_Length",
]

DISPLAY_COLUMNS = [
    "Player_Names",
    "Country",
    "Start_Year",
    "End_Year",
    "Matches",
    "Total_Runs",
    "Batting_Average",
    "Strike_Rate",
    "100's",
    "50's",
    "Career_Length",
]

RADAR_METRICS = ["Total_Runs", "Batting_Average", "Strike_Rate", "Matches", "100's", "50's"]

PLOT_TEMPLATE = "plotly_dark"
ACCENT_COLOR = "#38bdf8"
CHART_COLORS = ["#38bdf8", "#f472b6", "#34d399", "#facc15", "#a78bfa", "#fb7185", "#22d3ee", "#fb923c"]


st.set_page_config(page_title="ODI Batting Performance Dashboard", layout="wide")


def apply_custom_css() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at 12% 6%, rgba(56, 189, 248, .18), transparent 24%),
                radial-gradient(circle at 84% 12%, rgba(244, 114, 182, .18), transparent 24%),
                radial-gradient(circle at 52% 92%, rgba(52, 211, 153, .13), transparent 30%),
                linear-gradient(135deg, #08111f 0%, #101827 46%, #172033 100%);
            background-attachment: fixed;
        }
        .block-container { padding-top: 1.25rem; padding-bottom: 2rem; max-width: 1440px; }
        [data-testid="stSidebar"] {
            background: rgba(8, 17, 31, .94);
            border-right: 1px solid rgba(148, 163, 184, .22);
        }
        div[data-testid="stMetric"] {
            border: 1px solid rgba(56, 189, 248, .25);
            border-radius: 8px;
            padding: .9rem 1rem;
            background: linear-gradient(135deg, rgba(15, 23, 42, .94), rgba(30, 41, 59, .82));
            box-shadow: 0 16px 36px rgba(0, 0, 0, .24);
        }
        div[data-testid="stMetric"] label, div[data-testid="stMetric"] [data-testid="stMetricLabel"] {
            color: #bae6fd !important;
        }
        div[data-testid="stMetricValue"] {
            color: #f8fafc !important;
            white-space: normal !important;
            overflow-wrap: anywhere !important;
            line-height: 1.2 !important;
            font-size: clamp(1rem, 1.35vw, 1.35rem) !important;
        }
        div[data-testid="stMetricDelta"] svg {
            width: .8rem;
            height: .8rem;
        }
        div[data-testid="stMetric"] {
            min-height: 138px;
        }
        div[data-testid="stMetric"] + div,
        div[data-testid="stCaptionContainer"] {
            color: #cbd5e1 !important;
        }
        .kpi-card {
            border: 1px solid rgba(56, 189, 248, .25);
            border-radius: 8px;
            padding: .9rem 1rem;
            min-height: 146px;
            background: linear-gradient(135deg, rgba(15, 23, 42, .94), rgba(30, 41, 59, .82));
            box-shadow: 0 16px 36px rgba(0, 0, 0, .24);
        }
        .kpi-label {
            color: #bae6fd;
            font-size: .88rem;
            font-weight: 650;
            margin-bottom: .42rem;
        }
        .kpi-value {
            color: #f8fafc;
            font-size: clamp(1rem, 1.45vw, 1.38rem);
            font-weight: 800;
            line-height: 1.24;
            white-space: normal;
            overflow-wrap: anywhere;
            word-break: normal;
        }
        .kpi-detail {
            color: #86efac;
            font-size: .82rem;
            line-height: 1.25;
            margin-top: .55rem;
            overflow-wrap: anywhere;
        }
        .dashboard-title {
            color: #f8fafc;
            font-size: 2.35rem;
            font-weight: 850;
            margin-bottom: .15rem;
            letter-spacing: 0;
        }
        .dashboard-subtitle { color: #cbd5e1; font-size: 1rem; margin-bottom: 1rem; }
        h1, h2, h3, .stMarkdown, label, p {
            color: #e2e8f0;
        }
        .insight-box {
            border: 1px solid rgba(56, 189, 248, .24);
            border-radius: 8px;
            background: linear-gradient(135deg, rgba(15, 23, 42, .92), rgba(30, 41, 59, .78));
            padding: 1rem 1.1rem;
            margin-bottom: .75rem;
            box-shadow: 0 16px 36px rgba(0, 0, 0, .22);
            color: #e2e8f0;
        }
        .drill-box {
            border-left: 4px solid #38bdf8;
            background: rgba(14, 165, 233, .12);
            padding: .85rem 1rem;
            border-radius: 6px;
            margin-bottom: 1rem;
            color: #e0f2fe;
        }
        div[data-testid="stDataFrame"], div[data-testid="stPlotlyChart"] {
            border-radius: 8px;
            overflow: hidden;
        }
        div[data-testid="stPlotlyChart"] {
            border: 1px solid rgba(148, 163, 184, .20);
            background: linear-gradient(135deg, rgba(15, 23, 42, .88), rgba(24, 32, 51, .76));
            box-shadow: 0 18px 38px rgba(0, 0, 0, .25);
            padding: .35rem;
            margin-bottom: .9rem;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: .4rem;
            background: rgba(15, 23, 42, .62);
            border-radius: 8px;
            padding: .35rem;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 6px;
            color: #cbd5e1;
            background: rgba(30, 41, 59, .78);
            padding: .55rem .9rem;
        }
        .stTabs [aria-selected="true"] {
            color: #f8fafc;
            background: linear-gradient(135deg, #0ea5e9, #a855f7);
        }
        div.stButton > button, div[data-testid="stDownloadButton"] > button {
            border-radius: 7px;
            border: 1px solid rgba(56, 189, 248, .38);
            background: linear-gradient(135deg, #0284c7, #7c3aed);
            color: white;
            font-weight: 700;
        }
        div[data-baseweb="select"] > div, input, textarea {
            background-color: rgba(15, 23, 42, .90) !important;
            color: #f8fafc !important;
            border-color: rgba(148, 163, 184, .28) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def initialize_state() -> None:
    defaults = {
        "active_country": "All",
        "active_player": "All",
        "heatmap_x": "Matches",
        "heatmap_y": "Total_Runs",
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df["Player_Names"] = df["Player_Names"].astype(str).str.strip()
    df["Country"] = df["Country"].astype(str).str.strip()
    df["Career_Length"] = (df["End_Year"] - df["Start_Year"]).clip(lower=1)
    df["Runs_Per_Match"] = df["Total_Runs"] / df["Matches"].replace(0, pd.NA)
    df["Century_Rate"] = df["100's"] / df["Matches"].replace(0, pd.NA)
    return df


@st.cache_data
def summarize_country(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("Country", as_index=False)
        .agg(
            Players=("Player_Names", "count"),
            Total_Runs=("Total_Runs", "sum"),
            Avg_Runs=("Total_Runs", "mean"),
            Avg_Batting_Average=("Batting_Average", "mean"),
            Avg_Strike_Rate=("Strike_Rate", "mean"),
            Centuries=("100's", "sum"),
            Half_Centuries=("50's", "sum"),
        )
        .sort_values("Total_Runs", ascending=False)
        .round(2)
    )


@st.cache_data
def correlation_frame(df: pd.DataFrame) -> pd.DataFrame:
    return df[NUMERIC_COLUMNS].corr().round(2)


def format_number(value: float) -> str:
    return f"{value:,.0f}"


def kpi_card(container: Any, label: str, value: str, detail: str) -> None:
    container.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{escape(label)}</div>
            <div class="kpi-value">{escape(value)}</div>
            <div class="kpi-detail">{escape(detail)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def event_points(event: Any) -> list[dict[str, Any]]:
    if not event:
        return []
    if isinstance(event, dict):
        return event.get("selection", {}).get("points", [])
    selection = getattr(event, "selection", None)
    return getattr(selection, "points", []) if selection else []


def update_state_from_event(event: Any, key: str, point_field: str | None = None) -> None:
    points = event_points(event)
    if not points:
        return

    point = points[0]
    value = None
    customdata = point.get("customdata")
    if customdata:
        value = customdata[0]
    elif point_field:
        value = point.get(point_field)

    if value and st.session_state.get(key) != value:
        st.session_state[key] = value
        st.rerun()


def chart(fig: go.Figure, key: str) -> Any:
    return st.plotly_chart(
        style_figure(fig),
        use_container_width=True,
        key=key,
        on_select="rerun",
        selection_mode=("points", "box", "lasso"),
    )


def show_chart(fig: go.Figure) -> None:
    st.plotly_chart(style_figure(fig), use_container_width=True)


def style_figure(fig: go.Figure, height: int | None = None) -> go.Figure:
    has_slider = bool(fig.layout.sliders)
    title_x = fig.layout.title.x if fig.layout.title and fig.layout.title.x is not None else 0.02
    title_anchor = fig.layout.title.xanchor if fig.layout.title and fig.layout.title.xanchor else "left"
    legend_layout = (
        {
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.15,
            "xanchor": "right",
            "x": 1,
            "bgcolor": "rgba(15,23,42,.45)",
            "bordercolor": "rgba(148,163,184,.20)",
            "borderwidth": 1,
            "font": {"size": 8},
            "title": {"font": {"size": 9}},
            "itemwidth": 30,
            "itemsizing": "constant",
        }
        if has_slider
        else {
            "orientation": "h",
            "yanchor": "top",
            "y": -0.18,
            "xanchor": "center",
            "x": 0.5,
            "bgcolor": "rgba(15,23,42,.45)",
            "bordercolor": "rgba(148,163,184,.20)",
            "borderwidth": 1,
            "font": {"size": 8},
            "title": {"font": {"size": 9}},
            "itemwidth": 30,
            "itemsizing": "constant",
        }
    )
    margin = {"l": 28, "r": 28, "t": 150, "b": 130} if has_slider else {"l": 28, "r": 28, "t": 105, "b": 105}
    layout_updates = {
        "template": PLOT_TEMPLATE,
        "paper_bgcolor": "rgba(15,23,42,0.08)",
        "plot_bgcolor": "rgba(15,23,42,0.72)",
        "font": {"family": "Segoe UI, Arial, sans-serif", "color": "#e2e8f0"},
        "title": {
            "font": {"size": 19, "color": "#f8fafc"},
            "x": title_x,
            "xanchor": title_anchor,
            "y": 0.98,
            "yanchor": "top",
            "pad": {"b": 18},
        },
        "legend": legend_layout,
        "margin": margin,
        "colorway": CHART_COLORS,
    }
    if height:
        layout_updates["height"] = height
    fig.update_layout(**layout_updates)
    fig.update_xaxes(
        showgrid=True,
        gridcolor="rgba(148, 163, 184, .18)",
        zeroline=False,
        linecolor="rgba(226, 232, 240, .28)",
        tickfont={"color": "#cbd5e1"},
        title_font={"color": "#e2e8f0"},
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(148, 163, 184, .18)",
        zeroline=False,
        linecolor="rgba(226, 232, 240, .28)",
        tickfont={"color": "#cbd5e1"},
        title_font={"color": "#e2e8f0"},
    )
    return fig


def filter_controls(df: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    with st.sidebar:
        st.header("Global Filters")

        countries = st.multiselect(
            "Country filter",
            sorted(df["Country"].unique()),
            default=sorted(df["Country"].unique()),
        )

        country_options = ["All"] + sorted(countries)
        if st.session_state.active_country not in country_options:
            st.session_state.active_country = "All"
        selected_country = st.selectbox(
            "Drill-down country",
            country_options,
            index=country_options.index(st.session_state.active_country),
        )
        st.session_state.active_country = selected_country

        player_base = df[df["Country"].isin(countries)]
        if selected_country != "All":
            player_base = player_base[player_base["Country"] == selected_country]

        player_options = ["All"] + sorted(player_base["Player_Names"].unique())
        if st.session_state.active_player not in player_options:
            st.session_state.active_player = "All"
        selected_player = st.selectbox(
            "Drill-down player",
            player_options,
            index=player_options.index(st.session_state.active_player),
        )
        st.session_state.active_player = selected_player

        year_range = st.slider(
            "Career year range",
            int(df["Start_Year"].min()),
            int(df["End_Year"].max()),
            (int(df["Start_Year"].min()), int(df["End_Year"].max())),
        )

        min_runs = st.number_input(
            "Minimum runs",
            min_value=0,
            max_value=int(df["Total_Runs"].max()),
            value=0,
            step=250,
        )

        with st.expander("What-if filters", expanded=True):
            min_matches = st.slider("Minimum matches", 0, int(df["Matches"].max()), 0, step=10)
            min_average = st.slider("Minimum batting average", 0.0, float(df["Batting_Average"].max()), 0.0, step=1.0)
            min_strike = st.slider("Minimum strike rate", 0.0, float(df["Strike_Rate"].max()), 0.0, step=2.0)
            min_centuries = st.slider("Minimum centuries", 0, int(df["100's"].max()), 0)
            extra_matches = st.slider("What if every player got extra matches?", 0, 100, 0, step=5)

        if st.button("Reset drill-down", use_container_width=True):
            st.session_state.active_country = "All"
            st.session_state.active_player = "All"
            st.rerun()

    mask = (
        df["Country"].isin(countries)
        & (df["Start_Year"] >= year_range[0])
        & (df["End_Year"] <= year_range[1])
        & (df["Total_Runs"] >= min_runs)
        & (df["Matches"] >= min_matches)
        & (df["Batting_Average"] >= min_average)
        & (df["Strike_Rate"] >= min_strike)
        & (df["100's"] >= min_centuries)
    )

    if selected_country != "All":
        mask &= df["Country"] == selected_country
    if selected_player != "All":
        mask &= df["Player_Names"] == selected_player

    filtered = df.loc[mask].copy()
    filtered["Projected_Runs"] = filtered["Total_Runs"] + (filtered["Runs_Per_Match"].fillna(0) * extra_matches)

    country_text = "all countries" if selected_country == "All" else selected_country
    player_text = "all players" if selected_player == "All" else selected_player
    summary = f"{country_text}, {player_text}, {year_range[0]}-{year_range[1]}, min {min_runs:,} runs"
    return filtered, summary


def show_kpis(df: pd.DataFrame, full_df: pd.DataFrame) -> None:
    top_scorer = df.nlargest(1, "Total_Runs").iloc[0]
    best_average = df.nlargest(1, "Batting_Average").iloc[0]

    c1, c2, c3, c4 = st.columns([1, 1.45, 1.45, 1.2])
    kpi_card(
        c1,
        "Total Players",
        format_number(len(df)),
        f"{len(df) - len(full_df):+,} vs full dataset",
    )
    kpi_card(
        c2,
        "Top Scorer",
        f"{top_scorer['Player_Names']}",
        f"{top_scorer['Total_Runs']:,.0f} runs | {top_scorer['Total_Runs'] - full_df['Total_Runs'].max():+,.0f} vs all-time top",
    )
    kpi_card(
        c3,
        "Best Average",
        f"{best_average['Player_Names']}",
        f"{best_average['Batting_Average']:.2f} average | {best_average['Batting_Average'] - full_df['Batting_Average'].max():+.2f} vs all-time best",
    )
    kpi_card(
        c4,
        "Total Runs",
        format_number(df["Total_Runs"].sum()),
        f"{df['Total_Runs'].sum():,.0f} runs | {df['Total_Runs'].sum() / full_df['Total_Runs'].sum():.1%} of dataset",
    )

def smart_insights(df: pd.DataFrame) -> None:
    top = df.nlargest(1, "Total_Runs").iloc[0]
    best_avg = df.nlargest(1, "Batting_Average").iloc[0]
    best_sr = df.nlargest(1, "Strike_Rate").iloc[0]
    country = df["Country"].value_counts().idxmax()
    corr = df[["Matches", "Total_Runs"]].corr().iloc[0, 1] if len(df) > 1 else 0

    st.markdown(
        f"""
        <div class="insight-box">
        <b>Smart insights</b><br>
        {top['Player_Names']} leads the selected view with <b>{top['Total_Runs']:,}</b> runs.
        {best_avg['Player_Names']} owns the strongest batting average at <b>{best_avg['Batting_Average']:.2f}</b>,
        while {best_sr['Player_Names']} has the highest strike rate at <b>{best_sr['Strike_Rate']:.2f}</b>.
        The most represented country is <b>{country}</b>. Matches and total runs show a
        <b>{corr:.2f}</b> correlation in this filtered view.
        </div>
        """,
        unsafe_allow_html=True,
    )


def drilldown_panel(df: pd.DataFrame) -> None:
    selected_country = st.session_state.active_country
    selected_player = st.session_state.active_player

    if selected_player != "All" and not df.empty:
        player = df.iloc[0]
        st.markdown(
            f"""
            <div class="drill-box">
            <b>Career drill-down:</b> {player['Player_Names']} ({player['Country']}) played from
            {player['Start_Year']} to {player['End_Year']}, scoring {player['Total_Runs']:,} runs
            in {player['Matches']:,} matches at an average of {player['Batting_Average']:.2f}.
            </div>
            """,
            unsafe_allow_html=True,
        )
    elif selected_country != "All":
        st.markdown(
            f'<div class="drill-box"><b>Country drill-down:</b> Charts are focused on {selected_country}. Select a player bar or sidebar player for career-level detail.</div>',
            unsafe_allow_html=True,
        )


def top_players_bar(df: pd.DataFrame, metric: str, title: str, limit: int = 12) -> go.Figure:
    plot_df = df.nlargest(min(limit, len(df)), metric).sort_values(metric)
    fig = px.bar(
        plot_df,
        x=metric,
        y="Player_Names",
        orientation="h",
        text=metric,
        color="Country",
        custom_data=["Player_Names"],
        title=title,
        hover_data=DISPLAY_COLUMNS,
        color_discrete_sequence=CHART_COLORS,
    )
    fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    fig.update_layout(height=470, margin=dict(l=20, r=20, t=105, b=35), yaxis_title="")
    return fig


def country_bar(summary: pd.DataFrame, metric: str, title: str) -> go.Figure:
    plot_df = summary.nlargest(min(15, len(summary)), metric).sort_values(metric)
    fig = px.bar(
        plot_df,
        x=metric,
        y="Country",
        orientation="h",
        text=metric,
        custom_data=["Country"],
        title=title,
        hover_data=summary.columns,
        color=metric,
        color_continuous_scale=["#0f172a", "#0ea5e9", "#22c55e", "#facc15"],
    )
    fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    fig.update_layout(height=500, margin=dict(l=20, r=20, t=105, b=35), yaxis_title="", showlegend=False)
    return fig


def country_player_sunburst(df: pd.DataFrame) -> go.Figure:
    top_df = df.nlargest(min(60, len(df)), "Total_Runs").copy()
    top_df["Runs_Label"] = top_df["Total_Runs"].map(lambda value: f"{value:,.0f}")
    fig = px.sunburst(
        top_df,
        path=["Country", "Player_Names"],
        values="Total_Runs",
        color="Total_Runs",
        color_continuous_scale=[
            "#172033",
            "#164e63",
            "#0e7490",
            "#38bdf8",
            "#818cf8",
            "#a78bfa",
            "#f0abfc",
        ],
        custom_data=["Country", "Player_Names", "Runs_Label", "Batting_Average", "Strike_Rate", "100's", "50's"],
        title="Runs Share Sunburst: Country to Top ODI Batters",
    )
    fig.update_traces(
        marker=dict(
            line=dict(color="rgba(15, 23, 42, .95)", width=2),
        ),
        insidetextorientation="radial",
        texttemplate="<b>%{label}</b><br>%{percentParent:.1%}",
        textfont=dict(color="#f8fafc", size=15),
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Share of parent: %{percentParent:.1%}<br>"
            "Share of total: %{percentRoot:.1%}<br>"
            "Total runs: %{customdata[2]}<br>"
            "Country: %{customdata[0]}<br>"
            "Player: %{customdata[1]}<br>"
            "Average: %{customdata[3]:.2f}<br>"
            "Strike rate: %{customdata[4]:.2f}<br>"
            "100s: %{customdata[5]} | 50s: %{customdata[6]}<extra></extra>"
        ),
    )
    fig.update_layout(
        height=640,
        margin=dict(l=20, r=20, t=110, b=35),
        coloraxis_colorbar=dict(
            title=dict(text="Total Runs", font=dict(color="#f8fafc")),
            tickfont=dict(color="#cbd5e1"),
        ),
    )
    return fig


def country_distribution(df: pd.DataFrame, metric: str) -> go.Figure:
    top_countries = df["Country"].value_counts().head(10).index
    plot_df = df[df["Country"].isin(top_countries)].copy()
    fig = px.box(
        plot_df,
        x="Country",
        y=metric,
        color="Country",
        points="all",
        hover_name="Player_Names",
        hover_data=DISPLAY_COLUMNS,
        title=f"{metric.replace('_', ' ')} Spread by Country",
        color_discrete_sequence=CHART_COLORS,
    )
    fig.update_layout(height=520, margin=dict(l=25, r=25, t=105, b=75), showlegend=False)
    fig.update_xaxes(tickangle=-30)
    return fig


def performance_dot_plot(df: pd.DataFrame) -> go.Figure:
    plot_df = df.nlargest(min(12, len(df)), "Total_Runs").copy()

    # Normalize
    for col in RADAR_METRICS:
        max_val = df[col].max() if df[col].max() != 0 else 1
        plot_df[col] = (plot_df[col] / max_val) * 100

    # Melt
    plot_df = plot_df.melt(
        id_vars=["Player_Names"],
        value_vars=RADAR_METRICS,
        var_name="Metric",
        value_name="Score"
    )

    fig = px.scatter(
        plot_df,
        x="Metric",
        y="Score",
        color="Player_Names",
        size="Score",
        title="Player Performance Dot Comparison (Normalized %)",
        color_discrete_sequence=CHART_COLORS,
    )

    fig.update_layout(
        height=550,
        yaxis_title="Performance (%)",
        xaxis_title="Metrics",
    )

    return fig


def projected_runs_chart(df: pd.DataFrame) -> go.Figure:
    if "Projected_Runs" not in df.columns:
        df = df.copy()
        df["Projected_Runs"] = df["Total_Runs"]
    plot_df = df.nlargest(min(15, len(df)), "Projected_Runs").sort_values("Projected_Runs")
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=plot_df["Total_Runs"],
            y=plot_df["Player_Names"],
            orientation="h",
            name="Current Runs",
            marker_color="#38bdf8",
            customdata=plot_df[["Player_Names"]],
            hovertemplate="<b>%{y}</b><br>Current runs: %{x:,.0f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            x=plot_df["Projected_Runs"] - plot_df["Total_Runs"],
            y=plot_df["Player_Names"],
            orientation="h",
            name="What-if Extra Runs",
            marker_color="#f472b6",
            customdata=plot_df[["Player_Names"]],
            hovertemplate="<b>%{y}</b><br>Projected gain: %{x:,.0f}<extra></extra>",
        )
    )
    fig.update_layout(
        title="What-if Projection: Current Runs plus Extra-Match Estimate",
        barmode="stack",
        height=520,
        margin=dict(l=25, r=25, t=105, b=45),
        yaxis_title="",
        xaxis_title="Runs",
    )
    return fig


def active_trend(df: pd.DataFrame, title: str) -> go.Figure:
    years = []
    for row in df.itertuples():
        years.extend(range(int(row.Start_Year), int(row.End_Year) + 1))
    trend = pd.Series(years).value_counts().sort_index().rename_axis("Year").reset_index(name="Active Players")
    fig = px.line(trend, x="Year", y="Active Players", markers=True, title=title)
    fig.update_traces(line=dict(width=3, color="#0f766e"))
    fig.update_layout(height=420, margin=dict(l=25, r=25, t=100, b=40))
    return fig


def animated_era_scatter(df: pd.DataFrame) -> go.Figure:
    plot_df = df.copy()

    # Create Era buckets
    plot_df["Era"] = ((plot_df["Start_Year"] // 5) * 5).astype(int).astype(str)

    # Padding
    x_padding = max(2, (plot_df["Batting_Average"].max() - plot_df["Batting_Average"].min()) * 0.08)
    y_padding = max(5, (plot_df["Strike_Rate"].max() - plot_df["Strike_Rate"].min()) * 0.08)

    # Normalize bubble size (IMPORTANT for better visuals)
    plot_df["Size"] = plot_df["Total_Runs"] / plot_df["Total_Runs"].max() * 60

    fig = px.scatter(
        plot_df.sort_values("Era"),
        x="Batting_Average",
        y="Strike_Rate",
        animation_frame="Era",
        animation_group="Player_Names",
        color="Country",
        size="Size",
        size_max=50,
        opacity=0.75,
        hover_name="Player_Names",
        color_discrete_sequence=CHART_COLORS,
        range_x=[
            max(0, float(plot_df["Batting_Average"].min() - x_padding)),
            float(plot_df["Batting_Average"].max() + x_padding),
        ],
        range_y=[
            max(0, float(plot_df["Strike_Rate"].min() - y_padding)),
            float(plot_df["Strike_Rate"].max() + y_padding),
        ],
    )

    # ðŸ”¥ Custom hover (clean + professional)
    fig.update_traces(
        marker=dict(
            line=dict(color="white", width=1.5)
        ),
        hovertemplate="""
        <b>%{hovertext}</b><br>
        Country: %{marker.color}<br>
        Batting Avg: %{x:.2f}<br>
        Strike Rate: %{y:.2f}<br>
        Runs: %{customdata[0]:,}<br>
        Era: %{frame}<extra></extra>
        """,
        customdata=plot_df[["Total_Runs"]]
    )

    # ðŸŽ¯ Layout improvements
    fig.update_layout(
        height=620,
        margin=dict(l=60, r=40, t=100, b=80),

        # TITLE (properly centered)
        title=dict(
            text="Animated Batting Style by Era<br><sup>Evolution of batting average vs strike rate</sup>",
            x=0.5,
            xanchor="center",
            y=0.95,
            font=dict(size=24)
        ),

        # AXES
        xaxis=dict(
            title="Batting Average",
            gridcolor="rgba(255,255,255,0.08)",
            zeroline=False
        ),
        yaxis=dict(
            title="Strike Rate",
            gridcolor="rgba(255,255,255,0.08)",
            zeroline=False
        ),

        # LEGEND (clean + centered under title)
        legend=dict(
            title="Country",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=11)
        ),

        # SMOOTH ANIMATION
        transition=dict(duration=400),
    )

    # ðŸŽ¬ Fix animation controls
    if fig.layout.updatemenus:
        fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 600
        fig.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = 400

        fig.layout.updatemenus[0].direction = "left"
        fig.layout.updatemenus[0].pad = dict(r=10, t=70)

    # ðŸŽšï¸ Slider improvements
    if fig.layout.sliders:
        fig.layout.sliders[0].currentvalue.prefix = "Era: "
        fig.layout.sliders[0].pad = dict(t=40)
        fig.layout.sliders[0].len = 0.8

    return fig

def performance_scatter(df: pd.DataFrame, x: str, y: str, title: str) -> go.Figure:
    fig = px.scatter(
        df,
        x=x,
        y=y,
        color="Country",
        size="Total_Runs",
        hover_name="Player_Names",
        hover_data=DISPLAY_COLUMNS,
        custom_data=["Player_Names"],
        title=title,
        size_max=38,
        color_discrete_sequence=CHART_COLORS,
    )
    fig.update_layout(height=560, margin=dict(l=25, r=25, t=110, b=45), legend_title_text="Country")
    return fig


def comparison_chart(df: pd.DataFrame) -> go.Figure:
    default_players = df.nlargest(min(4, len(df)), "Total_Runs")["Player_Names"].tolist()

    selected = st.multiselect(
        "Compare players",
        sorted(df["Player_Names"].unique()),
        default=default_players,
        max_selections=6,
    )

    player_df = df[df["Player_Names"].isin(selected)].copy()

    if player_df.empty:
        fig = go.Figure()
        fig.update_layout(title="Select players to compare")
        return fig

    # Normalize values
    norm_df = player_df.copy()
    for col in RADAR_METRICS:
        max_val = df[col].max() if df[col].max() != 0 else 1
        norm_df[col] = (norm_df[col] / max_val) * 100

    # Convert to long format
    plot_df = norm_df.melt(
        id_vars=["Player_Names"],
        value_vars=RADAR_METRICS,
        var_name="Metric",
        value_name="Score"
    )

    fig = px.bar(
        plot_df,
        x="Metric",
        y="Score",
        color="Player_Names",
        barmode="group",
        text="Score",
        title="Player Comparison (Normalized %)",
        color_discrete_sequence=CHART_COLORS,
    )

    fig.update_traces(texttemplate="%{text:.0f}%", textposition="outside")

    fig.update_layout(
        height=550,
        yaxis_title="Performance (%)",
        xaxis_title="Metrics",
    )

    return fig


def correlation_heatmap(df: pd.DataFrame) -> go.Figure:
    corr = correlation_frame(df)
    fig = px.imshow(
        corr,
        text_auto=True,
        zmin=-1,
        zmax=1,
        aspect="auto",
        color_continuous_scale=["#7f1d1d", "#1e293b", "#0f766e"],
        title="Interactive Correlation Heatmap",
    )
    fig.update_traces(customdata=[[(x, y) for x in corr.columns] for y in corr.index])
    fig.update_layout(height=640, margin=dict(l=25, r=25, t=110, b=45))
    return fig


def show_correlation_drilldown(df: pd.DataFrame) -> None:
    c1, c2 = st.columns([1, 1])
    with c1:
        heat_event = chart(correlation_heatmap(df), "correlation_heatmap")
    points = event_points(heat_event)
    if points:
        point = points[0]
        st.session_state.heatmap_x = point.get("x", st.session_state.heatmap_x)
        st.session_state.heatmap_y = point.get("y", st.session_state.heatmap_y)

    with c2:
        x_metric = st.selectbox("Scatter X metric", NUMERIC_COLUMNS, index=NUMERIC_COLUMNS.index(st.session_state.heatmap_x))
        y_metric = st.selectbox("Scatter Y metric", NUMERIC_COLUMNS, index=NUMERIC_COLUMNS.index(st.session_state.heatmap_y))
        st.session_state.heatmap_x = x_metric
        st.session_state.heatmap_y = y_metric
        scatter_event = chart(
            performance_scatter(df, x_metric, y_metric, f"Scatter Drill-down: {x_metric} vs {y_metric}"),
            "correlation_scatter",
        )
        update_state_from_event(scatter_event, "active_player")


def overview_tab(df: pd.DataFrame, full_df: pd.DataFrame, summary_text: str) -> None:
    st.subheader(f"Overview: {summary_text}")
    smart_insights(df)
    drilldown_panel(df)

    c1, c2 = st.columns(2)
    with c1:
        country_event = chart(country_bar(summarize_country(df), "Total_Runs", "Cross-filter: Select a Country"), "country_runs_bar")
        update_state_from_event(country_event, "active_country")
    with c2:
        player_event = chart(top_players_bar(df, "Total_Runs", "Cross-filter: Select a Player"), "top_runs_bar")
        update_state_from_event(player_event, "active_player")

    sunburst_event = chart(country_player_sunburst(df), "country_player_sunburst")
    update_state_from_event(sunburst_event, "active_country")

    c3, c4 = st.columns(2)
    with c3:
        show_chart(active_trend(df, "Career Activity Trend"))
    with c4:
        show_chart(animated_era_scatter(df))


def country_tab(df: pd.DataFrame, summary_text: str) -> None:
    st.subheader(f"Country Analysis: {summary_text}")
    summary = summarize_country(df)

    c1, c2 = st.columns(2)
    with c1:
        event = chart(country_bar(summary, "Players", "Player Count by Country"), "country_count_bar")
        update_state_from_event(event, "active_country")
    with c2:
        fig = px.scatter(
            summary,
            x="Avg_Strike_Rate",
            y="Avg_Batting_Average",
            size="Total_Runs",
            color="Country",
            hover_name="Country",
            custom_data=["Country"],
            hover_data=["Players", "Total_Runs", "Centuries", "Half_Centuries"],
            title="Country Efficiency Map",
            size_max=55,
            color_discrete_sequence=CHART_COLORS,
        )
        fig.update_layout(height=500, margin=dict(l=25, r=25, t=110, b=45))
        event = chart(fig, "country_efficiency")
        update_state_from_event(event, "active_country")

    metric = st.selectbox(
        "Country distribution metric",
        ["Total_Runs", "Batting_Average", "Strike_Rate", "Matches", "100's"],
    )
    show_chart(country_distribution(df, metric))

    st.dataframe(summary, use_container_width=True, hide_index=True)


def player_tab(df: pd.DataFrame, summary_text: str) -> None:
    st.subheader(f"Player Analysis: {summary_text}")
    c1, c2 = st.columns([1, 1])
    with c1:
        show_chart(comparison_chart(df))
    with c2:
        scatter_event = chart(
            performance_scatter(df, "Matches", "Total_Runs", "Interactive Scatter: Matches vs Runs"),
            "matches_runs_scatter",
        )
        update_state_from_event(scatter_event, "active_player")

    c3, c4 = st.columns(2)
    with c3:
        event = chart(top_players_bar(df, "Batting_Average", "Top Batting Averages"), "avg_player_bar")
        update_state_from_event(event, "active_player")
    with c4:
        event = chart(top_players_bar(df, "Strike_Rate", "Top Strike Rates"), "sr_player_bar")
        update_state_from_event(event, "active_player")

    c5, c6 = st.columns([1, 1])
    with c5:
        show_chart(performance_dot_plot(df))
    with c6:
        projection_event = chart(projected_runs_chart(df), "projected_runs_chart")
        update_state_from_event(projection_event, "active_player")


def explorer_tab(df: pd.DataFrame) -> None:
    st.subheader("Enhanced Data Explorer")
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        search = st.text_input("Search player or country", "")
    with c2:
        sort_col = st.selectbox("Sort by", DISPLAY_COLUMNS, index=DISPLAY_COLUMNS.index("Total_Runs"))
    with c3:
        ascending = st.toggle("Ascending", value=False)

    explorer_df = df.copy()
    if search:
        needle = search.strip().lower()
        explorer_df = explorer_df[
            explorer_df["Player_Names"].str.lower().str.contains(needle)
            | explorer_df["Country"].str.lower().str.contains(needle)
        ]

    explorer_df = explorer_df.sort_values(sort_col, ascending=ascending)
    st.download_button(
        "Download explorer view",
        explorer_df.to_csv(index=False).encode("utf-8"),
        "odi_batting_explorer_view.csv",
        "text/csv",
        use_container_width=True,
    )
    st.dataframe(explorer_df[DISPLAY_COLUMNS + ["Projected_Runs"]], use_container_width=True, hide_index=True)


def main() -> None:
    apply_custom_css()
    initialize_state()
    df = load_data()
    filtered_df, summary_text = filter_controls(df)

    st.markdown('<div class="dashboard-title">ODI Batting Performance Command Center</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="dashboard-subtitle">Cross-filtered Plotly dashboard with drill-downs, what-if controls, radar comparison, correlation analysis, and smart insights.</div>',
        unsafe_allow_html=True,
    )

    if filtered_df.empty:
        st.warning("No records match the active filters. Relax the sidebar or reset the drill-down.")
        return

    with st.sidebar:
        st.download_button(
            "Download filtered dataset",
            filtered_df.to_csv(index=False).encode("utf-8"),
            "filtered_odi_batting_dataset.csv",
            "text/csv",
            use_container_width=True,
        )

    show_kpis(filtered_df, df)
    st.divider()

    overview, country, player, correlations, explorer = st.tabs(
        ["Overview", "Country Analysis", "Player Analysis", "Correlation Drill-down", "Data Explorer"]
    )

    with overview:
        overview_tab(filtered_df, df, summary_text)
    with country:
        country_tab(filtered_df, summary_text)
    with player:
        player_tab(filtered_df, summary_text)
    with correlations:
        show_correlation_drilldown(filtered_df)
    with explorer:
        explorer_tab(filtered_df)


if __name__ == "__main__":
    main()

