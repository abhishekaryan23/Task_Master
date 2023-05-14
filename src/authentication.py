import streamlit as st
from .database import db
from .helpers import create_new_user, create_task, find_tasks_by_status, update_task_status, login, change_password, admin_user_exists
from .session_state import SessionState
from datetime import datetime
from pymongo import DESCENDING


def display_login_page():
    if admin_user_exists():
        email = st.text_input("Email", "")
        password = st.text_input("Password", type="password")

    if not admin_user_exists():
        st.info("No admin user exists. Please create an initial admin user.")
        admin_email = st.text_input("Admin Email", "")
        admin_password = st.text_input("Admin Password", type="password")
        admin_confirm_password = st.text_input("Confirm Admin Password", type="password")

        create_admin_btn = st.button("Create Admin")

        if create_admin_btn:
            if admin_password == admin_confirm_password:
                create_new_user({"email": admin_email, "password": admin_password, "role": "admin"})
                st.success("Admin user created successfully!")
                st.experimental_rerun()
            else:
                st.error("Passwords do not match. Please try again.")
    else:
        login_btn = st.button("Login")

        if login_btn:
            user = login(email, password)

            if user:
                st.session_state.logged_in = True
                st.session_state.user = user
                st.experimental_rerun()
            else:
                st.error("Invalid email or password.")


def display_password_change_section(email):
    st.sidebar.subheader("Change Password")
    change_password_btn = st.sidebar.button("Change Password")

    if change_password_btn:
        st.sidebar.markdown("---")  # Add a horizontal line for separation
        st.sidebar.subheader("Reset Password")
        current_password = st.sidebar.text_input("Current Password", type="password", key="current_password")
        new_password = st.sidebar.text_input("New Password", type="password", key="new_password")
        confirm_password = st.sidebar.text_input("Confirm New Password", type="password", key="confirm_password")
        reset_password_btn = st.sidebar.button("Reset Password")

        if reset_password_btn:
            success, message = change_password(email, current_password, new_password, confirm_password)
            if success:
                st.sidebar.success(message)
            else:
                st.sidebar.error(message)