import streamlit as st
from .database import db
from .helpers import create_new_user, create_task, find_tasks_by_status, update_task_status, login, change_password, admin_user_exists
from .session_state import SessionState
from datetime import datetime
from pymongo import DESCENDING
from .authentication import display_password_change_section
from .tasks import display_task



def display_user_dashboard(email):
    st.sidebar.header("User Panel")
    st.sidebar.write(f"Welcome, {email}!")

    st.subheader("My Tasks")
    hide_completed_tasks = st.checkbox("Hide completed tasks", key="user_hide_completed", value=True)
    tasks = list(db.tasks.find({"assigned_to": st.session_state.user["email"]}))
    for idx, task in enumerate(tasks):
        if not (hide_completed_tasks and task["status"] == "completed"):
            display_task(task, email, task_index=idx)

    display_password_change_section(st.session_state.user["email"])

    st.sidebar.write("")  # Add some space before the logout button
    st.sidebar.write("")  # Add more space (repeat as needed)
    st.sidebar.write("")
    logout_btn = st.sidebar.button("Logout", key="user_logout")
    if logout_btn:
        st.session_state.logged_in = False
        st.session_state.user = None
        st.experimental_rerun()