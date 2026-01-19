import pandas as pd
import plotly.express as px

def draw_ticket_lg(df):
    df = df.copy()

    df["created_at"] = pd.to_datetime(df["created_at"])
    df["resolved_at"] = pd.to_datetime(df["resolved_at"], errors="coerce")

    created_weekly = (
        df.groupby(pd.Grouper(key="created_at", freq="W"))
          .size()
          .reset_index(name="Created")
          .rename(columns={"created_at": "week"})
    )

    resolved_weekly = (
        df[df["resolved_at"].notna()]
        .groupby(pd.Grouper(key="resolved_at", freq="W"))
        .size()
        .reset_index(name="Resolved")
        .rename(columns={"resolved_at": "week"})
    )

    weekly_df = (
        pd.merge(created_weekly, resolved_weekly, on="week", how="outer")
        .fillna(0)
        .sort_values("week")
    )

    # keep only last 5 weeks
    weekly_df = weekly_df.tail(5)

    fig = px.line(
        weekly_df,
        x="week",
        y=["Created", "Resolved"],
        markers=True,
        labels={
            "value": "Number of Tickets",
            "week": "Week",
            "variable": "Status"
        },
        title=" "
    )

    fig.update_yaxes(
        tickmode="linear",
        tick0=0,
        dtick=1
    )

    fig.update_layout(
        title_x=0.5,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=420,
        legend_title_text=""
    )

    return fig


def draw_ticket_breakdown_pie(df, criteria, period):
    df = df.copy()

    df["created_at"] = pd.to_datetime(df["created_at"])

    now = pd.Timestamp.now()

    if period == "This Week":
        start = (now - pd.Timedelta(days=now.weekday())).normalize()
        df = df[df["created_at"] >= start]

    elif period == "Last Week":
        start = (now - pd.Timedelta(days=now.weekday() + 7)).normalize()
        end = start + pd.Timedelta(days=7)
        df = df[(df["created_at"] >= start) & (df["created_at"] < end)]

    chart_data = (
        df[criteria]
        .value_counts()
        .reset_index()
    )
    chart_data.columns = [criteria, "count"]

    fig = px.pie(
        chart_data,
        values="count",
        names=criteria,
        hole=0.5
    )

    fig.update_traces(textinfo="percent+label")

    fig.update_layout(
        height=360,
        showlegend=True,
        margin=dict(t=40, b=20, l=20, r=20)
    )

    return fig
