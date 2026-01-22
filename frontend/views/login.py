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
        email = st.text_input("Email",placeholder="Enter company email")
        password = st.text_input("Password",type="password",placeholder="Enter password")
        login = st.form_submit_button("Login")

    if login:
        if email.strip() == "":
            st.error("Please enter email")
            st.stop()
        if password.strip() == "":
            st.error("Please enter password")
            st.stop()
        payload = {
            "username" : email,
            "password" : password
        }
        try:
            response = requests.post("http://127.0.0.1:8000/login/",data=payload)
            if response.status_code == 200:
                data = response.json()
                st.session_state["access_token"] = data["access_token"]
                st.session_state["current_emp"] = data["emp_id"]
                st.session_state["current_emp_name"] = data["emp_name"]
                st.session_state["access_level"] = data["access"]
                st.rerun()
            else:
                try:
                    error_details = response.json().get("detail","Unknown Error")
                except Exception as e:
                    error_details = "Internal Server Error"
                st.error(f"❌ {error_details}")
        except Exception as e:
            st.error(f"❌ An unexpected error occured {e}")