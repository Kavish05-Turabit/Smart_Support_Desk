import streamlit as st
import requests
import pandas as pd

st.markdown('<p style="font-family:sans-serif; ' \
'color:Purple; text-align:left; font-size: 62px;">' \
'Smart Support System</p>'
, unsafe_allow_html=True)

headers = {"Authorization" : f"Bearer {st.session_state.access_token}"}

if "customer_page" not in st.session_state:
    st.session_state.customer_page = "customer_full_view"
if "selected_customer" not in st.session_state:
    st.session_state.selected_customer = None


# VIEW SHOWING ALL CUSTOMERS ADN THEIR DETAILS


if st.session_state.customer_page == "customer_full_view":
    ct1,ct2,ct3 = st.columns([4.2,10,1.85])
    with ct1:
        st.title("Customers",text_alignment="left")
    with ct3:
        st.markdown(f'<br>',unsafe_allow_html=True)
        if st.button(label = "Create",icon=":material/add:"):
            st.session_state.customer_page = "customer_update_view"
            st.rerun()
    response = requests.get("http://127.0.0.1:8000/customers/",headers=headers)
    if response.status_code == 200:
        df = pd.DataFrame(response.json())
    else:
        st.warning(body="Connection Error")

    customers_df = st.dataframe(
        df,
        on_select="rerun",
        selection_mode="single-row",
        width="stretch",
        hide_index=True
    )

    if len(customers_df.selection.rows) > 0:
        index = customers_df.selection.rows[0]
        st.session_state.selected_customer = df.iloc[index].to_dict()
        st.session_state.customer_page = "customer_one_view"
        st.rerun()


# SINGLE CUSTOMER VIEW WITH UPDATE AND DELETE BUTTON


if st.session_state.customer_page == "customer_one_view":
    st.title("Customer Details",text_alignment="left")

    cb1,cb2,cb3 = st.columns([2,9,1.15])
    with cb1:
        if st.button(label = "Back",icon=":material/arrow_back:"):
            st.session_state.customer_page = "customer_full_view"
            st.session_state.selected_customer = None
            st.rerun()
    
    with cb3:
        if st.button(label="Update"):
            st.session_state.customer_page = "customer_update_view"
            st.rerun()

    cur_cust = st.session_state.selected_customer

    with st.container(width="stretch",border=True):
        cc1 , cc2 = st.columns([1,1])
        with cc1:
            st.markdown(f"**Customer Name**")
            st.code(" ".join([cur_cust["first_name"],cur_cust["last_name"]]))
            st.markdown(f"**Company**")
            st.code(cur_cust["company"])
            st.markdown(f"**Created by**")
            st.code(cur_cust["created_by"])

        with cc2:
            st.markdown(f"**Email**")
            st.code(cur_cust["email"])
            st.markdown(f"**Phone**")
            st.code(cur_cust["phone"])


# FORM FOR CUSTOMER CREATION AND UPDATION


if st.session_state.customer_page == "customer_update_view":
    cbu1,cbu2,cbu3 = st.columns([2,9,1.3])
    with cbu1:
        if st.button(label = "Home",icon=":material/home:"):
            st.session_state.customer_page = "customer_full_view"
            st.session_state.selected_customer = None
            st.rerun()
    
    with cbu3:
        if st.session_state.selected_customer:
            if st.button(label = "Back",icon=":material/arrow_back:"):
                st.session_state.customer_page = "customer_one_view"
                st.rerun()

    customer = st.session_state.selected_customer or {}
    form_values = {
        "first_name": customer.get("first_name", ""),
        "last_name": customer.get("last_name", ""),
        "company": customer.get("company", ""),
        "email": customer.get("email", ""),
        "phone": customer.get("phone", "")
    }

    with st.form(key="customer_form"):
        cf1,cf2 = st.columns(2)

        with cf1:
            f_name = st.text_input("First Name",value=form_values["first_name"])
            email = st.text_input("Email",value=form_values["email"])
            company = st.text_input("Company", value=form_values["company"])

        with cf2:
            l_name = st.text_input("Last Name",value=form_values["last_name"])
            phone = st.text_input("Phone", value=form_values["phone"])
        
        submit_button = st.form_submit_button("Submit")

        if submit_button:
            new_customer_data = {
                "first_name": f_name,
                "last_name": l_name,
                "email": email,
                "company": company,
                "phone": phone
            }

            if st.session_state.selected_customer:
                requests.put(
                    f"http://127.0.0.1:8000/customers/{customer.get('customer_id')}/",
                    json=new_customer_data,
                    headers=headers
                )
            else:
                requests.post(
                    "http://127.0.0.1:8000/customers/",
                    json=new_customer_data,
                    headers=headers
                )

            st.session_state.customer_page = "customer_full_view"
            st.session_state.selected_customer = None
            st.rerun()