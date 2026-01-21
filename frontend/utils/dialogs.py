import streamlit as st
import requests

import streamlit as st
import requests

@st.dialog("Update Ticket Status")
def open_status_dialog(ticket_id, new_status, headers):
    st.write(f"Mark ticket as **{new_status}**?")
    note_content = st.text_area("Add a note (optional):", placeholder="Reason for status change...")
    
    if st.button("Confirm Update", type="primary"):
        
        status_payload = {"status": new_status}
        status_res = requests.put(
            f"http://127.0.0.1:8000/tickets/{ticket_id}/",
            json=status_payload,
            headers=headers
        )

        if status_res.status_code == 200:
            # 2. If a note was written, post it using your existing Note API
            if note_content.strip():
                note_payload = { "content": f"Status changed to {new_status}. Note: {note_content}"}
                requests.post(
                    f"http://127.0.0.1:8000/notes/{ticket_id}", 
                    json=note_payload, 
                    headers=headers
                )
            
            st.success(f"Ticket updated to {new_status}!")
            st.rerun()
            
        else:
            st.error("Failed to update status.")