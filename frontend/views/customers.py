import streamlit as st
import requests
import pandas as pd

st.markdown('<p style="font-family:sans-serif; ' \
'color:Purple; text-align:left; font-size: 62px;">' \
'Smart Support System</p>'
, unsafe_allow_html=True)
st.title("Customers",text_alignment="left")

headers = {"Authorization" : f"Bearer {st.session_state.access_token}"}

if "customer_page" not in st.session_state:
    st.session_state.customer_page = "customer_full_view"
if "selected_customer" not in st.session_state:
    st.session_state.selected_customer = None


# VIEW SHOWING ALL CUSTOMERS ADN THEIR DETAILS


if st.session_state.customer_page == "customer_full_view":
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

    if st.button(label = "Create",icon=":material/add:"):
        st.session_state.customer_page = "customer_update_view"
        st.rerun()


# SINGLE CUSTOMER VIEW WITH UPDATE AND DELETE BUTTON


if st.session_state.customer_page == "customer_one_view":
    if st.button(label = "Back",icon=":material/arrow_back:"):
        st.session_state.customer_page = "customer_full_view"
        st.session_state.selected_customer = None
        st.rerun()

    tdf = pd.DataFrame([st.session_state.selected_customer])
    st.dataframe(tdf)

    if st.button(label="Update"):
        st.session_state.customer_page = "customer_update_view"
        st.rerun()


# FORM FOR CUSTOMER CREATION AND UPDATION


if st.session_state.customer_page == "customer_update_view":
    if st.button(label = "Home",icon=":material/home:"):
        st.session_state.customer_page = "customer_full_view"
        st.session_state.selected_customer = None
        st.rerun()
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