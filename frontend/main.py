import streamlit as st
import requests
import pandas as pd
st.set_page_config(layout="wide",page_title="Smart Support Desk")

# st.title("Smart Support System",text_alignment="center")
st.markdown('<p style="font-family:sans-serif; color:Purple; text-align:center; font-size: 62px;">Smart Support System</p>', unsafe_allow_html=True)

login_page = st.Page("views/login.py",title="Login",icon=":material/login:")
dashboard_page = st.Page("views/dashboard.py",title="Dashboard",icon=":material/home:")

if "access_token" not in st.session_state:
    pages = st.navigation([login_page])
else:
    pages = st.navigation([
        dashboard_page
    ])

pages.run()