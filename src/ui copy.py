import streamlit as st
from .database import db
from .helpers import create_new_user, create_task, find_tasks_by_status, update_task_status
from .session_state import SessionState

def run_app():
    st.set_page_config(page_title="Task Management")

    st.title("Task Management App")

    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        display_login_page()
    else:
        if st.session_state.user["role"] == "admin":
            display_admin_dashboard()
        elif st.session_state.user["role"] == "user":
            display_user_dashboard(st.session_state.user["email"])

        logout_btn = st.button("Logout")

        if logout_btn:
            st.session_state.logged_in = False
            st.session_state.user = None

def display_login_page():
    email = st.text_input("Email", "")
    password = st.text_input("Password", type="password")

    login_btn = st.button("Login")

    if login_btn:
        user = db.users.find_one({"email": email, "password": password})

        if user:
            st.session_state.logged_in = True
            st.session_state.user = user
        else:
            st.error("Invalid email or password.")



def display_admin_dashboard():
    st.sidebar.header("Admin Panel")
    st.sidebar.write("Welcome, Admin!")

    admin_options = ["Create User", "Create Task", "Monitor Tasks", "Fetch Tasks by Status"]
    admin_option = st.sidebar.radio("Options", admin_options)

    if admin_option == "Create User":
        st.subheader("Create New User")

        new_email = st.text_input("New User Email", "")
        new_password = st.text_input("New User Password", type="password")
        role = st.selectbox("Role", ["admin", "user"])

        create_user_btn = st.button("Create User")

        if create_user_btn:
            create_new_user({"email": new_email, "password": new_password, "role": role})
            st.success("User created successfully!")

    elif admin_option == "Create Task":
        st.subheader("Create New Task")

        task_name = st.text_input("Task Name", "")
        task_description = st.text_area("Task Description", "")
        assign_to = st.selectbox("Assign To", [st.session_state.user["email"]] + [user["email"] for user in db.users.find({"role": "user"})])

        create_task_btn = st.button("Create Task")

        if create_task_btn:
            create_task({"name": task_name, "description": task_description, "assigned_to": assign_to, "status": "pending"})
            st.success("Task created successfully!")

    elif admin_option == "Monitor Tasks":
        st.subheader("Monitor All Tasks")
        tasks = db.tasks.find()

        for task in tasks:
            display_task(task)

    elif admin_option == "Fetch Tasks by Status":
        st.subheader("Fetch Tasks by Status")

        status = st.selectbox("Select Status", ["pending", "in progress", "completed"])
        tasks = find_tasks_by_status(status)

        for task in tasks:
            display_task(task)

def display_user_dashboard(email):
    st.sidebar.header("User Panel")
    st.sidebar.write(f"Welcome, {email}!")

    st.subheader("My Tasks")
    tasks = list(db.tasks.find({"assigned_to": st.session_state.user["email"]}))


    for task in tasks:
        display_task(task, email)

def display_task(task, email=None):
    status_color = {
        "pending": "red",
        "in progress": "orange",
        "completed": "green"
    }
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"**Task**: {task['name']}")  
    with col2:
        st.markdown(f"**Assigned to**: {task['assigned_to']}")
    with col3:
        st.markdown(f"**Description**: {task['description']}")
    with col4:
        st.markdown(f'<p style="color:{status_color[task["status"]]}">**Status**: {task["status"]}</p>', unsafe_allow_html=True)

    if email:
        new_status = st.selectbox(f"Update status for {task['name']}", ["pending", "in progress", "completed"], key=task["_id"])

        if new_status != task["status"]:
            if new_status == "pending":
                comment = st.text_area("Please provide a reason for moving the task back to pending:", key=f"comment-{task['_id']}")

            update_task_btn = st.button("Update Task Status", key=task["_id"])

            if update_task_btn:
                if new_status == "pending":
                    if comment.strip():
                        update_task_status(str(task["_id"]), new_status, comment)
                        st.success("Task status updated successfully!")
                    else:
                        st.error("Please provide a reason for moving the task back to pending.")
                else:
                    update_task_status(str(task["_id"]), new_status)
                    st.success("Task status updated successfully!")
