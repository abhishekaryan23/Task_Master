import streamlit as st
from .database import db
from .helpers import create_new_user, create_task, find_tasks_by_status, update_task_status, login, change_password, admin_user_exists
from .session_state import SessionState, get_state
from datetime import datetime
from pymongo import DESCENDING
from .authentication import display_password_change_section
from .tasks import display_task




def display_admin_dashboard():
    st.sidebar.header("Admin Panel")
    st.sidebar.write("Welcome, Admin!")

    admin_options = {
        "My Tasks": "📋", 
        "Create User": "👤", 
        "Create Task": "➕", 
        "Monitor Tasks": "🔍", 
        "Fetch Tasks by Status": "🔃", 
        "Fetch Tasks by User": "👥"
    }

    state = get_state()

    if 'selected_option' not in state:
        state['selected_option'] = 'My Tasks'

    for option, emoji in admin_options.items():
        if st.sidebar.button(f"{emoji} {option}"):
            state['selected_option'] = option

    st.sidebar.write(f"You selected: {state['selected_option']}")

    selected_option = state['selected_option']

    if selected_option == "My Tasks":
        st.subheader("My Tasks")
        hide_completed_tasks = st.checkbox("Hide completed tasks", key="admin_hide_completed", value=True)
        tasks = list(db.tasks.find({"assigned_to": st.session_state.user["email"]}))
        for idx, task in enumerate(tasks):
            if not (hide_completed_tasks and task["status"] == "completed"):
                display_task(task, st.session_state.user["email"], is_admin=True, allow_status_change=True, task_index=idx)

    elif selected_option == "Create User":
        st.subheader("Create New User")

        new_email = st.text_input("New User Email", "")
        new_password = st.text_input("New User Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        role = st.selectbox("Role", ["admin", "user"])

        create_user_btn = st.button("Create User")

        if create_user_btn:
            if new_password == confirm_password:
                create_new_user({"email": new_email, "password": new_password, "role": role})
                st.success("User created successfully!")
            else:
                st.error("Passwords do not match. Please try again.")

    elif selected_option == "Create Task":
        st.subheader("Create New Task")

        task_name = st.text_input("Task Name", "")
        task_description = st.text_area("Task Description", "")
        assign_to = st.selectbox("Assign To", [st.session_state.user["email"]] + [user["email"] for user in db.users.find({"role": "user"})])

        create_task_btn = st.button("Create Task")

        if create_task_btn:
            create_task({"name": task_name, "description": task_description, "assigned_to": assign_to, "status": "pending"})
            st.success("Task created successfully!")

    elif selected_option == "Monitor Tasks":
        st.subheader("Monitor All Tasks")
        col1, col2 = st.columns(2)  # Create two columns
        with col1:
            hide_completed_tasks = st.checkbox("Hide completed tasks", value=True)
        with col2:
            with st.container():
                sort_by_days_passed = st.checkbox("Sort tasks by days passed", value=False, key="sort_by_days_passed")


    
        tasks = db.tasks.find().sort("created_at", DESCENDING if sort_by_days_passed else None)

        if hide_completed_tasks:
            tasks = [task for task in tasks if task["status"] != "completed"]

        for idx, task in enumerate(tasks):
            display_task(task, st.session_state.user["email"], is_admin=True, allow_status_change=False, task_index=idx)

    elif selected_option == "Fetch Tasks by Status":
        st.subheader("Fetch Tasks by Status")

        status = st.selectbox("Select Status", ["pending", "in progress", "completed"])
        tasks = find_tasks_by_status(status)

        for idx, task in enumerate(tasks):
            display_task(task, st.session_state.user["email"], is_admin=True, allow_status_change=False, task_index=idx)

    elif selected_option == "Fetch Tasks by User":
        st.subheader("Fetch Tasks by User")

        user_email = st.selectbox("Select User", [st.session_state.user["email"]] + [user["email"] for user in db.users.find()])
        tasks = db.tasks.find({"assigned_to": user_email})

        for idx, task in enumerate(tasks):
            display_task(task, st.session_state.user["email"], is_admin=True, allow_status_change=False, task_index=idx)
    
    display_password_change_section(st.session_state.user["email"])

    st.sidebar.write("")  # Add some space before the logout button
    st.sidebar.write("")  # Add more space (repeat as needed)
    st.sidebar.write("")
    logout_btn = st.sidebar.button("Logout", key="admin_logout")
    if logout_btn:
        st.session_state.logged_in = False
        st.session_state.user = None
        st.experimental_rerun()