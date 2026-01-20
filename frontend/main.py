import streamlit as st
import requests
import pandas as pd
st.set_page_config(layout="wide",page_title="Smart Support Desk")

# st.title("Smart Support System",text_alignment="center")

login_page = st.Page("views/login.py",title="Login",icon=":material/login:")
dashboard_page = st.Page("views/dashboard.py",title="Dashboard",icon=":material/analytics:")
employee_page = st.Page("views/employee.py",title="Employees",icon=":material/support_agent:")
customer_page = st.Page("views/customers.py",title="Customers",icon=":material/group:")
ticket_page = st.Page("views/tickets.py",title="Tickets",icon=":material/task_alt:")
homepage_page = st.Page("views/homepage.py",title="Homepage",icon=":material/home:")


if "access_token" not in st.session_state:
    pages = st.navigation([login_page])
else:
    if st.session_state.access_level == "admin":
        pages = st.navigation([
            dashboard_page,
            homepage_page,
            employee_page,
            ticket_page,
            customer_page,
        ])
    else:
        pages = st.navigation([
            homepage_page,
            ticket_page,
            customer_page,
        ])

pages.run()