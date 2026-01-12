import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.title("Dashboard")

headers = {"Authorization" : f"Bearer {st.session_state["access_token"]}"}
response = requests.get("http://127.0.0.1:8000/tickets/",headers=headers)

if response.status_code == 200:
    df = pd.DataFrame(response.json())
else:
    st.warning(body="Connection Error",icon=":warning:")

criteria_map = {
    "Priority": "priority",
    "Status": "status",
    "Type": "ticket_type"
}

selected_label = st.radio(
    "Select Breakdown Criteria:",
    list(criteria_map.keys()),
    horizontal=True
)

selected_column = criteria_map[selected_label]

chart_data = df[selected_column].value_counts().reset_index()
chart_data.columns = [selected_column, "count"]

# 4. Create the Donut Chart
fig = px.pie(
    chart_data, 
    values="count", 
    names=selected_column, 
    hole=0.5, # This creates the 'Donut' shape (0 is a pie, 1 is empty)
    title=f"Distribution by {selected_label}"
)
fig.update_traces(textinfo='percent+label')

st.plotly_chart(fig, use_container_width=True)