import streamlit as st
import requests
import pandas as pd

st.markdown('<p style="font-family:sans-serif; ' \
'color:Purple; text-align:left; font-size: 62px;">' \
'Smart Support System</p>'
, unsafe_allow_html=True)

headers = {"Authorization" : f"Bearer {st.session_state.access_token}"}

if "employee_page" not in st.session_state:
    st.session_state.employee_page = "employee_full_view"
if "selected_employee" not in st.session_state:
    st.session_state.selected_employee = None


# VIEW SHOWING ALL EMPLOYEES And THEIR DETAILS


if st.session_state.employee_page == "employee_full_view":
    ct1,ct2,ct3 = st.columns([4.2,10,1.85])
    with ct1:
        st.title("Employees",text_alignment="left")
    with ct3:
        st.markdown(f'<br>',unsafe_allow_html=True)
        if st.button(label = "Create",icon=":material/add:"):
            st.session_state.employee_page = "employee_update_view"
            st.rerun()

    response = requests.get("http://127.0.0.1:8000/employees/",headers=headers)
    if response.status_code == 200:
        df = pd.DataFrame(response.json())
    else:
        st.warning(body="Connection Error")

    employees_df = st.dataframe(
        df,
        on_select="rerun",
        selection_mode="single-row",
        width='stretch',
        hide_index=True
    )

    if len(employees_df.selection.rows) > 0:
        index = employees_df.selection.rows[0]
        st.session_state.selected_employee = df.iloc[index].to_dict()
        st.session_state.employee_page = "employee_one_view"
        st.rerun()


# SINGLE EMPLOYEE VIEW WITH UPDATE AND DELETE BUTTON


if st.session_state.employee_page == "employee_one_view":

    cb1,cb2,cb3 = st.columns([2,9,1.15])
    with cb1:
        if st.button(label = "Back",icon=":material/arrow_back:"):
            st.session_state.employee_page = "employee_full_view"
            st.session_state.selected_employee = None
            st.rerun()
    
    with cb3:
        if st.button(label="Update"):
            st.session_state.employee_page = "employee_update_view"
            st.rerun()

    cur_emp = st.session_state.selected_employee
    
    with st.container(width="stretch",border=True):
        ce1 , ce2 = st.columns([1,1])
        with ce1:
            st.markdown(f"**Employee Name**")
            st.code(" ".join([cur_emp["first_name"],cur_emp["last_name"]]))
            st.markdown(f"**Access level**")
            st.code(cur_emp["access_level"].upper())
        with ce2:
            st.markdown(f"**Email**")
            st.code(cur_emp["email"])
            st.markdown(f"**Phone**")
            st.code(cur_emp["phone"])


# FORM FOR EMPLOYEE CREATION AND UPDATION


if st.session_state.employee_page == "employee_update_view":
    cbu1,cbu2,cbu3 = st.columns([2,9,1.3])
    with cbu1:
        if st.button(label = "Home",icon=":material/home:"):
            st.session_state.employee_page = "employee_full_view"
            st.session_state.selected_employee = None
            st.rerun()

    with cbu3:
        if st.session_state.selected_employee:
            if st.button(label = "Back",icon=":material/arrow_back:"):
                st.session_state.employee_page = "employee_one_view"
                st.rerun()

    employee = st.session_state.selected_employee or {}
    form_values = {
        "first_name": employee.get("first_name", ""),
        "last_name": employee.get("last_name", ""),
        "access_level": employee.get("access_level", ""),
        "email": employee.get("email", ""),
        "phone": employee.get("phone", ""),
        "index" : 0 if employee.get("access_level") == "admin" else 1
    }

    with st.form(key="employee_form"):
        cf1,cf2 = st.columns(2)

        with cf1:
            f_name = st.text_input("First Name",value=form_values["first_name"])
            email = st.text_input("Email",value=form_values["email"])
            access_level = st.selectbox("Access Level",options=["admin","agent"],index=form_values["index"])

        with cf2:
            l_name = st.text_input("Last Name",value=form_values["last_name"])
            password = ""
            if not st.session_state.selected_employee:
                password = st.text_input("Password", type="password")
            phone = st.text_input("Phone", value=form_values["phone"])
        
        submit_button = st.form_submit_button("Submit")

        if submit_button:
            new_employee_data = {
                "first_name": f_name,
                "last_name": l_name,
                "email": email,
                "access_level": access_level,
                "phone": phone
            }

            if st.session_state.selected_employee:
                requests.put(
                    f"http://127.0.0.1:8000/employees/{employee.get('employee_id')}/",
                    json=new_employee_data,
                    headers=headers
                )
            else:
                new_employee_data["password_hash"] = password
                requests.post(
                    "http://127.0.0.1:8000/employees/",
                    json=new_employee_data,
                    headers=headers
                )

            st.session_state.employee_page = "employee_full_view"
            st.session_state.selected_employee = None
            st.rerun()