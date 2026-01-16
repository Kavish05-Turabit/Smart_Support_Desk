import streamlit as st
import requests
import pandas as pd

st.markdown('<p style="font-family:sans-serif; ' \
'color:Purple; text-align:left; font-size: 62px;">' \
'Smart Support System</p>'
, unsafe_allow_html=True)

headers = {"Authorization" : f"Bearer {st.session_state.access_token}"}

if "ticket_page" not in st.session_state:
    st.session_state.ticket_page = "ticket_full_view"
if "selected_ticket" not in st.session_state:
    st.session_state.selected_ticket = None


# VIEW SHOWING ALL TICKETS And THEIR DETAILS


if st.session_state.ticket_page == "ticket_full_view":
    ct1,ct2,ct3 = st.columns([4,10,1.85])
    with ct1:
        st.title("Tickets",text_alignment="left")
    with ct3:
        st.markdown(f'<br>',unsafe_allow_html=True)
        if st.button(label = "Create",icon=":material/add:"):
            st.session_state.ticket_page = "ticket_update_view"
            st.rerun()
    response = requests.get("http://127.0.0.1:8000/tickets/",headers=headers)
    if response.status_code == 200:
        df = pd.DataFrame(response.json())
    else:
        st.warning(body="Connection Error")

    tickets_df = st.dataframe(
        df,
        on_select="rerun",
        selection_mode="single-row",
        width="stretch",
        hide_index=True
    )

    if len(tickets_df.selection.rows) > 0:
        index = tickets_df.selection.rows[0]
        st.session_state.selected_ticket = df.fillna(0).iloc[index].to_dict()
        st.session_state.ticket_page = "ticket_one_view"
        st.rerun()


# SINGLE TICKET VIEW WITH UPDATE AND DELETE BUTTON


if st.session_state.ticket_page == "ticket_one_view":

    cur_ticket = st.session_state.selected_ticket

    cb1,cb2,cb3 = st.columns([2,9,1.15])
    with cb1:
        if st.button(label = "Back",icon=":material/arrow_back:"):
            st.session_state.ticket_page = "ticket_full_view"
            st.session_state.selected_ticket = None
            st.rerun()
    
    with cb3:
        if st.button(label="Update"):
            if st.session_state.current_emp == cur_ticket["created_by_id"] or st.session_state.access_level == "admin":
                st.session_state.ticket_page = "ticket_update_view"
                st.rerun()
    
    with st.container(width="stretch",border=True):
        st.markdown(f"**Ticket Title**")
        st.code(cur_ticket["title"])
        st.markdown(f"**Description**")
        st.code(cur_ticket["description"],language=None)

        ct1 , ct2 = st.columns([1,1])
        with ct1:
            st.markdown(f"**Ticket Type**")
            st.code(cur_ticket["ticket_type"])
            st.markdown(f"**Priority**")
            st.code(cur_ticket["priority"])

        with ct2:
            st.markdown(f"**Status**")
            st.code(cur_ticket["status"])
            st.markdown(f"**Ticket created at**")
            st.code(cur_ticket["created_at"])

        ctt1,ctt2,ctt3 = st.columns([1,1,1])
        with ctt1:
            st.markdown(f"**Customer**")
            st.code(cur_ticket["customer_id"])
        with ctt2:
            st.markdown(f"**Created By**")
            st.code(cur_ticket["created_by_id"])
        with ctt3:
            st.markdown(f"**Assigned To**")
            st.code(cur_ticket["assignee_id"])


# FORM FOR TICKET CREATION AND UPDATION


if st.session_state.ticket_page == "ticket_update_view":
    cbu1,cbu2,cbu3 = st.columns([2,9,1.3])
    with cbu1:
        if st.button(label = "Home",icon=":material/home:"):
            st.session_state.ticket_page = "ticket_full_view"
            st.session_state.selected_ticket = None
            st.rerun()
    
    with cbu3:
        if st.session_state.selected_ticket:
            if st.button(label = "Back",icon=":material/arrow_back:"):
                st.session_state.ticket_page = "ticket_one_view"
                st.rerun()

    ticket = st.session_state.selected_ticket or {}

    ttypes = ["Inquiry","Bug","Feature Request","Billing","Access"]
    priorities = ["Critical","High","Medium","Low"]
    form_values = {
        "title" : ticket.get("title",""),
        "description" : ticket.get("description",""),
        "ticket_type" : ticket.get("ticket_type","Inquiry"),
        "customer_id" : int(ticket.get("customer_id") or 0 ),
        "assignee_id" : int(ticket.get("assignee_id") or 0 ),
        "priority" : ticket.get("priority","Medium")
    }

    with st.form(key="ticket_form"):
        
        title = st.text_input("Title",value=form_values["title"])
        desc = st.text_area("Description",value=form_values["description"])

        cf1,cf2 = st.columns(2)

        with cf1:
            ttype = st.selectbox("Type of Ticket",options=ttypes,index=ttypes.index(form_values["ticket_type"]))
            cid = st.number_input("Customer",value=form_values["customer_id"])

        with cf2:
            priority = st.selectbox("Priority",options=priorities,index=priorities.index(form_values["priority"]))

        if not st.session_state.selected_ticket:
            assign_self = st.checkbox("Assign Ticket to Yourself?")
        else:
            assign = st.number_input("Assign To (0 = Unassigned)",value=form_values["assignee_id"])

        submit_button = st.form_submit_button("Submit")

        if submit_button:
            final_assignee = None
            if st.session_state.selected_ticket:
                final_assignee = assign if assign > 0 else None
            else:
                final_assignee = st.session_state.current_emp if assign_self else None

            new_ticket_data = {
                "title" : title,
                "description" : desc,
                "ticket_type" : ttype,
                "customer_id" : cid,
                "priority" : priority,
                "status" : ticket.get("status","Open"),
                "assignee_id" : final_assignee
            }

            if st.session_state.selected_ticket:
                requests.put(
                    f"http://127.0.0.1:8000/tickets/{ticket.get('ticket_id')}/",
                    json=new_ticket_data,
                    headers=headers
                )
            else:
                requests.post(
                    "http://127.0.0.1:8000/tickets/",
                    json=new_ticket_data,
                    headers=headers
                )
            
            st.session_state.ticket_page = "ticket_full_view"
            st.session_state.selected_ticket = None
            st.rerun()