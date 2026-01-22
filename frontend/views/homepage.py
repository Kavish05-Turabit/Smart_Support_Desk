import streamlit as st
import requests
import pandas as pd
from utils.dialogs import open_status_dialog

st.markdown('<p style="font-family:sans-serif; ' \
'color:Purple; text-align:left; font-size: 62px;">' \
'Smart Support System</p>'
, unsafe_allow_html=True)

headers = {"Authorization" : f"Bearer {st.session_state.access_token}"}

response = requests.get("http://127.0.0.1:8000/dashboard/",headers=headers)
if response.status_code == 200:
    tdf = pd.DataFrame(response.json()["tickets"])
    edf = pd.DataFrame(response.json()["Emp_details"])
else:
    st.warning(body="Connection Error")

current_emp_tickets = tdf[tdf["assignee_id"] == st.session_state.current_emp]

st.header("Overview")
c1,c2,c3,c4 = st.columns(4)

with c1:
    st.metric(label="Current Tickets",value=current_emp_tickets[current_emp_tickets["status"] != "Closed"].shape[0],width="stretch")
with c2:
    st.metric(label="Critical Tickets",value=current_emp_tickets[current_emp_tickets["priority"] == "critical"].shape[0],width="stretch")
with c3:
    st.metric(label="Tickets closed by you",value=current_emp_tickets[current_emp_tickets["status"] == "Closed"].shape[0],width="stretch")
with c4:
    tickets_left = current_emp_tickets[current_emp_tickets["status"] == "Closed"].shape[0]
    total_tickets = current_emp_tickets.shape[0]
    work_done = (tickets_left/total_tickets) * 100
    st.metric(label="Work Done",value=f"{work_done:.1f}%",width="stretch")


st.header("Your Tickets")
tab1,tab2 = st.tabs(["Current Tickets" , "Closed Tickets"])

with tab1:
    if (current_emp_tickets[current_emp_tickets["status"] != "Closed"]).empty:
        st.subheader("No Tickets currently assigned to you.")
    else:
        for index,ticket in current_emp_tickets.iterrows():
            t_id = ticket['ticket_id']
            if ticket["status"] != "Closed":
                with st.container(border=True):
                    col1,col2 = st.columns([4,1])

                    with col1:
                        st.markdown(f"**{t_id} - {ticket['title']}**")
                        st.caption(f"Priority - {ticket['priority']}    |    Status - {ticket['status']}")
                        desc = ticket.get("description" , "")
                        st.write(desc[:100] + "..." if len(desc) > 100 else desc)

                    with col2:
                        if st.button("View",key=f"b{t_id}",width="stretch"):
                            st.session_state.selected_ticket = ticket.fillna(0).to_dict()
                            st.session_state.ticket_page = "ticket_one_view"
                            st.switch_page("views/tickets.py")

                        if ticket["status"] == "In Progress":
                            if st.button("Mark as Done",key=f"m{t_id}",width="stretch",type="primary"):
                                open_status_dialog(ticket_id=t_id,new_status="Closed",headers=headers)
        
                        else:
                            if st.button("Open Ticket",key=f"s{t_id}",width="stretch",type="primary"):
                                open_status_dialog(ticket_id=t_id,new_status="In Progress",headers=headers)

with tab2:
    if (current_emp_tickets[current_emp_tickets["status"] == "Closed"]).empty:
        st.subheader("No Tickets resolved by you.")
    else:
        for index,ticket in current_emp_tickets.iterrows():
            t_id = ticket['ticket_id']
            if ticket["status"] == "Closed":
                with st.container(border=True):
                    col1,col2 = st.columns([4,1])

                    with col1:
                        st.markdown(f"**{t_id} - {ticket['title']}**")
                        st.caption(f"Priority - {ticket['priority']}    |    Status - {ticket['status']}")
                        desc = ticket.get("description" , "")
                        st.write(desc[:100] + "..." if len(desc) > 100 else desc)

                    with col2:
                        if st.button("View",key=f"b{t_id}",width="stretch"):
                            st.session_state.selected_ticket = ticket.fillna(0).to_dict()
                            st.session_state.ticket_page = "ticket_one_view"
                            st.switch_page("views/tickets.py")
