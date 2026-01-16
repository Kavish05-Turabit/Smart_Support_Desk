import streamlit as st
import requests
st.markdown('<p style="font-family:sans-serif; ' \
'color:Purple; text-align:center; font-size: 62px;">' \
'Smart Support System</p>'
, unsafe_allow_html=True)
st.title("Login to continue",text_alignment="center")

col1,col2,col3 = st.columns([2,3,2])

with col2:
    with st.form(key="Login Form"):
        email = st.text_input("Email",placeholder="admin@gmail.com")
        password = st.text_input("Password",type="password",placeholder="12345678")
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
            st.session_state["current_emp"] = data["emp_id"]
            st.session_state["access_level"] = data["access"]
            st.rerun()