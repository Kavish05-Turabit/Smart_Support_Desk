import streamlit as st
import requests
import pandas as pd
import plotly.express as px

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

    selected_column = criteria_map[selected_label]

    chart_data = df[selected_column].value_counts().reset_index()
    chart_data.columns = [selected_column, "count"]

    fig = px.pie(
        chart_data, 
        values="count", 
        names=selected_column, 
        hole=0.5,
    )
    fig.update_traces(textinfo='percent+label')

    st.plotly_chart(fig, width="content")

    ecol1, ecol2 = st.columns([10, 2], vertical_alignment="bottom")

    with ecol1:
        st.header("Employee Status")

    with ecol2:
        empB = st.button("View",width="stretch",key="view_employees")

    st.dataframe(edf,width="stretch")

    if empB:
        st.switch_page("views/employee.py")

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

    st.dataframe(df[["title","ticket_type","priority"]],width="stretch")

    if tckB:
        st.switch_page("views/tickets.py")