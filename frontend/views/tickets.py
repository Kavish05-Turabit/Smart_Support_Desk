import streamlit as st
import requests
import pandas as pd

st.markdown('<p style="font-family:sans-serif; ' \
'color:Purple; text-align:left; font-size: 62px;">' \
'Smart Support System</p>'
, unsafe_allow_html=True)
st.title("Tickets",text_alignment="left")

headers = {"Authorization" : f"Bearer {st.session_state.access_token}"}

if "ticket_page" not in st.session_state:
    st.session_state.ticket_page = "ticket_full_view"
if "selected_ticket" not in st.session_state:
    st.session_state.selected_ticket = None


if st.session_state.ticket_page == "ticket_full_view":
    response = requests.get("http://127.0.0.1:8000/tickets/",headers=headers)
    if response.status_code == 200:
        df = pd.DataFrame(response.json())
    else:
        st.warning(body="Connection Error")

    tickets_df = st.dataframe(
        df,
        on_select="rerun",
        selection_mode="single-row",
        width="stretch",
        hide_index=True
    )

    if len(tickets_df.selection.rows) > 0:
        index = tickets_df.selection.rows[0]
        st.session_state.selected_ticket = df.iloc[index].to_dict()
        st.session_state.ticket_page = "ticket_one_view"
        st.rerun()

if st.session_state.ticket_page == "ticket_one_view":
    if st.button(label = "Back",icon=":material/arrow_back:"):
        st.session_state.ticket_page = "ticket_full_view"
        st.session_state.selected_ticket = None
        st.rerun()

    tdf = pd.DataFrame([st.session_state.selected_ticket])
    st.dataframe(tdf)