import requests
import pandas as pd
import streamlit as st

WEB_URL = "https://script.google.com/macros/s/AKfycbxp6PWwP_0xSpPWLhdUyhBdxsO0upZ8cB3eqT7jzecFI4KimJ_jbX6MplAnkfxG8CfcwQ/exec"

st.title("Tenant Registry")

# --- Load Sheet ---
def load_sheet():
    r = requests.get(WEB_URL)
    r.raise_for_status()
    values = r.json()
    df = pd.DataFrame(values[1:], columns=values[0])
    return df

if "df" not in st.session_state:
    st.session_state.df = load_sheet()

# --- Add Tenant ---
st.subheader("Add Tenant")
with st.form(key="add_tenant_form"):  # unique key
    name = st.text_input("Resident Name")
    unit = st.text_input("Unit Number")
    email = st.text_input("Email")
    phone = st.text_input("Phone Number")
    submitted = st.form_submit_button("Add Tenant")
    if submitted:
        # Check for duplicates and append -i if needed
        base_name = name.strip()
        final_name = base_name
        i = 2
        existing_names = st.session_state.df["resident_name"].tolist()
        while final_name in existing_names:
            final_name = f"{base_name}-{i}"
            i += 1

        payload = {"action":"add_row",
                   "row":{"resident_name":final_name,
                          "unit_number":unit,
                          "email":email,
                          "phone_number":phone}}
        requests.post(WEB_URL, json=payload)
        st.success(f"Added: {final_name}")
        st.session_state.df = load_sheet()  # refresh data
        st.rerun()

# --- Delete Tenant ---
st.subheader("Delete Tenant")
if "selected_to_delete" not in st.session_state:
    st.session_state.selected_to_delete = []

st.session_state.selected_to_delete = st.multiselect(
    "Select tenant(s) to delete",
    st.session_state.df["resident_name"].tolist(),
    default=st.session_state.selected_to_delete,
    key="delete_multiselect"
)

confirm = st.checkbox("Confirm deletion")
if st.button("Delete Selected"):
    if st.session_state.selected_to_delete and confirm:
        for name in st.session_state.selected_to_delete:
            idx = st.session_state.df.index[st.session_state.df["resident_name"]==name][0] + 2
            requests.post(WEB_URL, json={"action":"delete_row","row_index":int(idx)})
        st.success("Deleted selected tenant(s)")
        st.session_state.df = load_sheet()
        st.session_state.selected_to_delete = []  # clear selection
    elif not st.session_state.selected_to_delete:
        st.warning("No tenant selected")
    elif not confirm:
        st.warning("Please confirm deletion")

# --- Show current tenants ---
st.subheader("Current Tenants")
st.table(st.session_state.df)
