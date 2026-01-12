import streamlit as st
import requests

st.title("Login to continue",text_alignment="center")

col1,col2,col3 = st.columns([1,2,1])

with col2:
    with st.form(key="Login Form"):
        email = st.text_input("Email")
        password = st.text_input("Password",type="password")
        login = st.form_submit_button("Login")

    if login:
        payload = {
            "username" : email,
            "password" : password
        }
        response = requests.post("http://127.0.0.1:8000/login/",data=payload)
        if response.status_code == 200:
            data = response.json()
            st.session_state["access_token"] = data["access_token"]
            st.rerun()