import streamlit as st
from .database import get_users_collection
from .helpers import create_new_user, create_task, find_tasks_by_status, update_task_status, login, change_password, admin_user_exists, load_lottie_file, get_task_collection
from .session_state import SessionState
from datetime import datetime
from pymongo import DESCENDING
# from .authentication import display_password_change_section
from .tasks import display_task
from streamlit_lottie import st_lottie
import json

# def display_user_dashboard(email):
#     st.sidebar.header("User Panel")
#     st.sidebar.write(f"Welcome, {email}!")

#     st.subheader("My Tasks")
#     hide_completed_tasks = st.checkbox("Hide completed tasks", key="user_hide_completed", value=True)
#     tasks = list(get_users_collection(st.session_state.company_name).find({"assigned_to": st.session_state.user["email"]}))
#     for idx, task in enumerate(tasks):
#         if not (hide_completed_tasks and task["status"] == "completed"):
#             display_task(task, email, task_index=idx)

#     display_password_change_section(st.session_state.user["email"], st.session_state.company_name)

#     st.sidebar.write("")  # Add some space before the logout button
#     st.sidebar.write("")  # Add more space (repeat as needed)
#     st.sidebar.write("")
#     logout_btn = st.sidebar.button("Logout", key="user_logout")
#     if logout_btn:
#         st.session_state.logged_in = False
#         st.session_state.user = None
#         st.experimental_rerun()

def display_user_dashboard(name):
    st.sidebar.header("User Panel")
    st.sidebar.write(f"Welcome, {name}!")

    # Add a selectbox for the navigation menu with emojis
    menu = ["📋 My Tasks", "👤 Profile"]
    choice = st.sidebar.selectbox("Menu", menu, key='user_dashboard_menu')

    if choice == "📋 My Tasks":
        st.subheader("My Tasks")
        hide_completed_tasks = st.checkbox("Hide completed tasks", key="admin_hide_completed", value=True)
        tasks = list(get_task_collection(st.session_state.company_name).find({"assigned_to": st.session_state.user["email"]}))
        
        # Check if there are any tasks assigned to the user
        if len(tasks) == 0:
            st.info("No tasks assigned to you.")
        else:
            for idx, task in enumerate(tasks):
                if not (hide_completed_tasks and task["status"] == "completed"):
                    display_task(task, st.session_state.user["email"], st.session_state.company_name, is_admin=False, allow_status_change=True, task_index=idx)

    elif choice == "👤 Profile":
        st.subheader("User Profile")

        # Create two columns
        col1, col2 = st.columns(2)

        # Display user details in the second column
        with col2:
            st.write("")
            st.write("")
            st.write("")
            st.write(f"**Name:** {st.session_state.user['name']}")
            st.write(f"**Email:** {st.session_state.user['email']}")
            st.write(f"**Company Name:** {st.session_state.company_name}")
            st.write(f"**Role:** {st.session_state.user['role']}")

            # Display password change section
            change_password_btn = st.button("Change Password")

            if change_password_btn or st.session_state.get('show_change_password_form', False):
                st.session_state['show_change_password_form'] = True  # Keep the form visible after submission
                st.subheader("Reset Password")

                with st.form(key='change_password_form'):
                    current_password = st.text_input("Current Password", type="password")
                    new_password = st.text_input("New Password", type="password")
                    confirm_password = st.text_input("Confirm New Password", type="password")
                    reset_password_btn = st.form_submit_button(label='Reset Password')  # Use form submit button here

                    if reset_password_btn:  # This will only be True when the form submit button is clicked
                        success, message = change_password(st.session_state.user['email'], current_password, new_password, confirm_password)
                        if success:
                            st.success(message)
                            st.session_state['show_change_password_form'] = False  # Hide the form after successful submission
                        else:
                            st.error(message)

        # Display Lottie animation in the first column
        with col1:
            lottie_json = load_lottie_file("./resources/profile.json")
            st_lottie(lottie_json, speed=1, height=200, key="profile_animation")

    st.sidebar.write("")  # Add some space before the logout button
    st.sidebar.write("")  # Add more space (repeat as needed)
    st.sidebar.write("")
    logout_btn = st.sidebar.button("Logout", key="user_logout")
    if logout_btn:
        st.session_state.clear()  # Clear all items from the session state
        # Re-initialize necessary attributes
        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.page = "Login"  # or any default page you want after logout
        st.experimental_rerun()