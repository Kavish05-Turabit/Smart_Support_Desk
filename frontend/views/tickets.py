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

cust_res = requests.get("http://127.0.0.1:8000/customers/", headers=headers)
emp_res = requests.get("http://127.0.0.1:8000/employees/", headers=headers)

all_customers = cust_res.json() if cust_res.status_code == 200 else []
all_employees = emp_res.json() if emp_res.status_code == 200 else []

unassigned_option = {"employee_id": 0, "first_name": "Unassigned", "last_name": ""}
all_employees.insert(0, unassigned_option)


# VIEW SHOWING ALL TICKETS And THEIR DETAILS


if st.session_state.ticket_page == "ticket_full_view":
    ct1,ct2,ct3 = st.columns([4,10,1.85])
    with ct1:
        st.title("Tickets",text_alignment="left")
    with ct3:
        st.markdown(f'<br>',unsafe_allow_html=True)
        if st.button(label = "Create",icon=":material/add:",type="primary"):
            st.session_state.ticket_page = "ticket_update_view"
            st.rerun()
    response = requests.get("http://127.0.0.1:8000/tickets/",headers=headers)
    if response.status_code == 200:
        df = pd.DataFrame(response.json())
    else:
        st.warning(body="Connection Error")

    col_names = {
        "ticket_id" : "ID",
        "title" : "Title",
        "ticket_type" : "Type",
        "priority" : "Priority",
        "status" : "Status",
        "assignee_id" : "Assigned To"
    }
    display_df = df[["ticket_id","title","ticket_type","priority","status","assignee_id"]].rename(columns=col_names).copy()

    tickets_df = st.dataframe(
        display_df,
        on_select="rerun",
        selection_mode="single-row",
        width="stretch",
        hide_index=True,
    )

    if len(tickets_df.selection.rows) > 0:
        index = tickets_df.selection.rows[0]
        st.session_state.selected_ticket = df.fillna(0).iloc[index].to_dict()
        st.session_state.ticket_page = "ticket_one_view"
        st.rerun()

    st.header("Tickets created by you")
    own_df = df[df["created_by_id"] == st.session_state.current_emp]
    own_display_df = own_df[["ticket_id","title","ticket_type","priority","status","assignee_id"]].rename(columns=col_names).copy()

    own_tickets_df = st.dataframe(
        own_display_df,
        on_select="rerun",
        selection_mode="single-row",
        width="stretch",
        hide_index=True
    )

    if len(own_tickets_df.selection.rows) > 0:
        index = own_tickets_df.selection.rows[0]
        st.session_state.selected_ticket = own_df.fillna(0).iloc[index].to_dict()
        st.session_state.ticket_page = "ticket_one_view"
        st.rerun()


# SINGLE TICKET VIEW WITH UPDATE AND DELETE BUTTON


if st.session_state.ticket_page == "ticket_one_view":

    cur_ticket = st.session_state.selected_ticket
    
    # Get Customer Name
    display_cust_name = str(cur_ticket["customer_id"])
    for c in all_customers:
        if c["customer_id"] == cur_ticket["customer_id"]:
            display_cust_name = f"{c['first_name']} {c['last_name']}"
            break

    # Get Assignee Name
    display_assignee_name = "Unassigned"
    for e in all_employees:
        if e["employee_id"] == cur_ticket["assignee_id"]:
            display_assignee_name = f"{e['first_name']} {e['last_name']}"
            break
            
    # Get Creator Name
    display_creator_name = str(cur_ticket["created_by_id"])
    for e in all_employees:
        if e["employee_id"] == cur_ticket["created_by_id"]:
            display_creator_name = f"{e['first_name']} {e['last_name']}"
            break

    cb1,cb2,cb3 = st.columns([2,9,1.15])
    with cb1:
        if st.button(label = "Back",icon=":material/arrow_back:"):
            st.session_state.ticket_page = "ticket_full_view"
            st.session_state.selected_ticket = None
            st.rerun()
    
    with cb3:
        if st.button(label="Update",type="primary"):
            if st.session_state.access_level == "admin":
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
            st.code(display_cust_name)
        with ctt2:
            st.markdown(f"**Created By**")
            st.code(display_creator_name)
        with ctt3:
            st.markdown(f"**Assigned To**")
            st.code(display_assignee_name)

        if st.session_state.current_emp == cur_ticket["created_by_id"] or st.session_state.access_level == "admin":
            if cur_ticket["assignee_id"] == 0 :
                if st.button("Assign to me"):
                    values = {
                        "assignee_id" : st.session_state.current_emp
                    }
                    requests.put(
                        f"http://127.0.0.1:8000/tickets/{cur_ticket['ticket_id']}/",
                        json=values,
                        headers=headers
                    )
                    response = requests.get(
                        f"http://127.0.0.1:8000/tickets/{cur_ticket['ticket_id']}/",
                        headers=headers
                    )
                    df = pd.DataFrame([response.json()])
                    st.session_state.selected_ticket = df.fillna(0).iloc[0].to_dict()
                    st.rerun()

    st.markdown(f"<h4>Notes</h4>",unsafe_allow_html=True)
    with st.container(width="stretch",key="ticket_notes",border=True):

        response = requests.get(
            f"http://127.0.0.1:8000/notes/{cur_ticket['ticket_id']}/",
            headers=headers
        )
        notes = response.json()
        if len(notes) != 0:
            for note in notes:
                with st.chat_message("human"):
                    st.write(note.get('author_name'))
                    st.write(note['content'])
                    st.caption(note['created_at'])
        else:
            st.write("No Notes yet")

    if (st.session_state.current_emp == cur_ticket["assignee_id"] or st.session_state.access_level == "admin") and cur_ticket["status"] != "Closed":
        content = st.chat_input("Add a note")
        if content:
            res = requests.post(
                f"http://127.0.0.1:8000/notes/{cur_ticket['ticket_id']}/",
                json={"content" : content},
                headers=headers
            )
            if res.status_code == 200:
                st.rerun()


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

    current_cust_id = int(ticket.get("customer_id", "0"))
    current_emp_id = int(ticket.get("assignee_id", "0"))

    cust_id,asgn_id = 0,0 
    for i,c in enumerate(all_customers):
        if c["customer_id"] == current_cust_id:
            cust_id = i
    for i,c in enumerate(all_employees):
        if c["employee_id"] == current_emp_id:
            asgn_id = i

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
            sel_cust = st.selectbox(
                "Customer",
                options=all_customers,
                index=cust_id,
                format_func= lambda x: f"{x['first_name']} {x['last_name']} ({x.get('company', '')})"
            )

        with cf2:
            priority = st.selectbox("Priority",options=priorities,index=priorities.index(form_values["priority"]))

        if not st.session_state.selected_ticket:
            assign_self = st.checkbox("Assign Ticket to Yourself?")
        else:
            sel_asgn = st.selectbox(
                "Assign To",
                options=all_employees,
                index=asgn_id,
                format_func=lambda x: "Unassigned" if x['employee_id'] == 0 else f"{x['first_name']} {x['last_name']}"
            )

        submit_button = st.form_submit_button("Submit")

        if submit_button:
            final_assignee = None
            if st.session_state.selected_ticket:
                assignee = sel_asgn["employee_id"]
                final_assignee = assignee if assignee > 0 else None
            else:
                final_assignee = st.session_state.current_emp if assign_self else None

            new_ticket_data = {
                "title" : title,
                "description" : desc,
                "ticket_type" : ttype,
                "customer_id" : sel_cust["customer_id"],
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