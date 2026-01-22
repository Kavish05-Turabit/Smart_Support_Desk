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

# Fetch Employees for "Created By" display
emp_res = requests.get("http://127.0.0.1:8000/employees/", headers=headers)
all_employees = emp_res.json() if emp_res.status_code == 200 else []


# --- VIEW SHOWING ALL CUSTOMERS AND THEIR DETAILS ---


if st.session_state.customer_page == "customer_full_view":
    ct1,ct2,ct3 = st.columns([4.2,10,1.85])
    with ct1:
        st.title("Customers",text_alignment="left")
    with ct3:
        st.markdown(f'<br>',unsafe_allow_html=True)
        if st.button(label = "Create",icon=":material/add:", type="primary"):
            st.session_state.customer_page = "customer_update_view"
            st.rerun()
            
    response = requests.get("http://127.0.0.1:8000/customers/",headers=headers)
    if response.status_code == 200:
        df = pd.DataFrame(response.json())
    else:
        st.warning(body="Connection Error")
        df = pd.DataFrame() # Fallback to avoid crashes

    if not df.empty:
        df["name"] = df["first_name"] + " " + df["last_name"]
        
        col_names = {
            "customer_id" : "ID",
            "name" : "Customer Name",
            "email" : "Email ID",
            "company" : "Company"
        }

        display_df = df[["customer_id","name","email","company"]].rename(columns=col_names)

        customers_df = st.dataframe(
            display_df,
            on_select="rerun",
            selection_mode="single-row",
            width="stretch",
            hide_index=True
        )

        if len(customers_df.selection.rows) > 0:
            index = customers_df.selection.rows[0]
            # FIX 1: fillna("") instead of 0 for text fields
            st.session_state.selected_customer = df.fillna("").iloc[index].to_dict()
            st.session_state.customer_page = "customer_one_view"
            st.rerun()

        st.header("Customers created by you")
        own_df = df[df["created_by"] == st.session_state.current_emp]
        
        if not own_df.empty:
            own_display_df = own_df[["customer_id","name","email","company"]].rename(columns=col_names)

            own_customers_df = st.dataframe(
                own_display_df,
                on_select="rerun",
                selection_mode="single-row",
                width="stretch",
                hide_index=True
            )

            if len(own_customers_df.selection.rows) > 0:
                index = own_customers_df.selection.rows[0]
                st.session_state.selected_customer = own_df.fillna("").iloc[index].to_dict()
                st.session_state.customer_page = "customer_one_view"
                st.rerun()
        else:
            st.info("You haven't created any customers yet.")
    else:
        st.info("No customers found.")


# --- SINGLE CUSTOMER VIEW WITH UPDATE BUTTON ---


if st.session_state.customer_page == "customer_one_view":
    st.title("Customer Details",text_alignment="left")

    cb1,cb2,cb3 = st.columns([2,9,1.15])
    with cb1:
        if st.button(label = "Back",icon=":material/arrow_back:"):
            st.session_state.customer_page = "customer_full_view"
            st.session_state.selected_customer = None
            st.rerun()
    
    with cb3:
        if st.button(label="Update", type="primary"):
            st.session_state.customer_page = "customer_update_view"
            st.rerun()

    cur_cust = st.session_state.selected_customer
    display_creator_name = str(cur_cust.get("created_by", "Unknown"))
    
    for e in all_employees:
        if e["employee_id"] == cur_cust.get("created_by"):
            display_creator_name = f"{e['first_name']} {e['last_name']}"
            break

    with st.container(width="stretch",border=True):
        cc1 , cc2 = st.columns([1,1])
        with cc1:
            st.markdown(f"**Customer Name**")
            st.code(f"{cur_cust['first_name']} {cur_cust['last_name']}")
            st.markdown(f"**Company**")
            st.code(cur_cust["company"])
            st.markdown(f"**Created by**")
            st.code(display_creator_name)

        with cc2:
            st.markdown(f"**Email**")
            st.code(cur_cust["email"])
            st.markdown(f"**Phone**")
            st.code(cur_cust["phone"])


# --- FORM FOR CUSTOMER CREATION AND UPDATION ---


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
    
    # FIX 2: Safe .get() with empty string defaults
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

            try:
                if st.session_state.selected_customer:
                    # Update
                    res = requests.put(
                        f"http://127.0.0.1:8000/customers/{customer.get('customer_id')}/",
                        json=new_customer_data,
                        headers=headers
                    )
                else:
                    # Create
                    res = requests.post(
                        "http://127.0.0.1:8000/customers/",
                        json=new_customer_data,
                        headers=headers
                    )

                if res.status_code in [200, 201]:
                    st.success("Customer saved successfully!")
                    st.session_state.customer_page = "customer_full_view"
                    st.session_state.selected_customer = None
                    st.rerun()

                elif res.status_code == 422:
                    error_data = res.json().get("detail", [])
                    if isinstance(error_data, list):
                        for err in error_data:
                            field = err["loc"][-1]
                            msg = err["msg"]
                            st.error(f"❌ {field.title()}: {msg}")
                            break
                    else:
                        st.error(f"❌ {error_data}")
                    st.stop()
                    
                else:
                    st.error(f"❌ Error {res.status_code}: {res.text}")
                    st.stop()

            except Exception as e:
                st.error(f"❌ Connection Error: {e}")
                st.stop()