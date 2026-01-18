import streamlit as st
import requests
import pandas as pd
import plotly.express as px

from utils.charts import draw_ticket_lg,draw_ticket_breakdown_pie

st.markdown('<p style="font-family:sans-serif; ' \
'color:Purple; text-align:left; font-size: 62px;">' \
'Smart Support System</p>'
, unsafe_allow_html=True)
st.title("Dashboard",text_alignment="left")

headers = {"Authorization" : f"Bearer {st.session_state.access_token}"}
response = requests.get("http://127.0.0.1:8000/dashboard/",headers=headers)

if response.status_code == 200:
    df = pd.DataFrame(response.json()["tickets"])
    edf = pd.DataFrame(response.json()["Emp_details"])
else:
    st.warning(body="Connection Error")

df["created_at"] = pd.to_datetime(df["created_at"])
df_recent = df.sort_values("created_at", ascending=False).head(5)

criteria_map = {
    "Priority": "priority",
    "Status": "status",
    "Type": "ticket_type"
}

col1,col2,col3 = st.columns([10,1,10])

with col1:
    st.header("Tickets this week")
    selected_label = st.radio(
        "Select Breakdown Criteria:",
        list(criteria_map.keys()),
        horizontal=True,
    )
    period = st.radio(
        "Time Period",
        ["This Week", "Last Week", "Overall"],
        horizontal=True
    )

    selected_column = criteria_map[selected_label]

    fig = draw_ticket_breakdown_pie(df,selected_column,period)
    fig.update_traces(textinfo='percent+label')
    st.plotly_chart(fig, width="content")

    st.header("Tickets Created vs Resolved")
    st.text("Last 5 weeks")
    fig_tck = draw_ticket_lg(df)
    st.plotly_chart(fig_tck,width="content")


with col3:
    st.header("Tickets Overview")
    row1,row2 = st.columns([1,1],vertical_alignment="bottom")
    with row1:
        st.metric(label="Total Tickets",value=df.shape[0],width="stretch")
        st.metric(label="Opened Tickets",value=len(df[df['status'] == 'Open']),width="stretch")

    with row2:
        st.metric(label="Closed Tickets",value=len(df[df['status'] == 'Closed']),width="stretch")
        st.metric(label="Assigned Tickets",value=len(df[df['status'] == 'In Progress']),width="stretch")

    tcol1, tcol2 = st.columns([10, 2], vertical_alignment="bottom")

    with tcol1:
        st.header("Recent Tickets")

    with tcol2:
        tckB = st.button("View",width="stretch",key="view_tickets")

    st.dataframe(df_recent[["title","ticket_type","priority"]],width="stretch")

    if tckB:
        st.switch_page("views/tickets.py")

    st.text("")
    st.text("")
    st.text("")
    ecol1, ecol2 = st.columns([10, 2], vertical_alignment="bottom")

    with ecol1:
        st.header("Employee Status")
        st.text("Assigned tickets per employee")

    with ecol2:
        empB = st.button("View",width="stretch",key="view_employees")

    edf["active_tickets"] = edf["open_count"] + edf["progress_count"]
    fig_emp = px.bar(
        edf,
        y="first_name", x="active_tickets",
        orientation='h',
        color="active_tickets", color_continuous_scale="Viridis",
        range_x=[0,10], range_color=[0, edf["active_tickets"].max()],
        labels={"first_name" : "Agent" , "active_tickets" : "Current Tickets"}
    )
    fig_emp.update_xaxes(tick0=1,dtick=1)
    st.plotly_chart(fig_emp,width="content")

    if empB:
        st.switch_page("views/employee.py")