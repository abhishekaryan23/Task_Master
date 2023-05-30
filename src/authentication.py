import streamlit as st
# from .database import db
from .helpers import create_new_user, create_task, find_tasks_by_status, update_task_status, login, change_password, admin_user_exists
from .session_state import SessionState, get_state
from datetime import datetime
from pymongo import DESCENDING
import time
from email_validator import validate_email, EmailNotValidError


def is_valid_mongodb_name(name):
    """Check if the input name is valid for MongoDB"""
    invalid_chars = ["$", ".", "\0"]
    return not any(char in name for char in invalid_chars) and not name.startswith('system.')


def display_login_page():
    st.subheader("Login / Signup")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Existing User Login")

        with st.form(key='login_form', clear_on_submit=True):
            email_login = st.text_input("Email", key='email_login')
            password_login = st.text_input("Password", type="password", key='password_login')
            login_btn = st.form_submit_button("Login")

            if login_btn:
                user = login(email_login.lower(), password_login)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.session_state.company_name = user['company_name']
                    st.session_state.is_first_login = user.get('is_first_login', False)
                    st.experimental_rerun()
                else:                        st.error("Invalid email or password, or no account exists for the particular user.")

        st.write("")  # Add some spacing
        signup_redirect_btn = st.button("New Signup for Your Project")
        if signup_redirect_btn:
            st.session_state.signup_redirect = True
            st.experimental_rerun()

    if st.session_state.get("signup_redirect", False):
        with col2:
            st.subheader("Signup")
            with st.form(key='signup_form', clear_on_submit=True):
                name_signup = st.text_input("Name", key='name_signup')  # Add name input field
                email_signup = st.text_input("Email", key='email_signup')
                password_signup = st.text_input("Password", type="password", key='password_signup')
                confirm_password = st.text_input("Confirm Password", type="password", key='confirm_password')
                company_name_input = st.text_input("Project Name", key='company_name')
                company_name = company_name_input.strip().replace(' ', '_')[:20]
                terms_conditions = st.checkbox("Accept terms and conditions", key='terms_conditions')

                if company_name and not is_valid_mongodb_name(company_name):
                    st.error("Invalid company name. The company name cannot contain '.', '$', null characters, or start with 'system.'")

                else:
                    signup_btn = st.form_submit_button("Signup")

                    if signup_btn:
                        try:
                            validated_email = validate_email(email_signup)
                        except EmailNotValidError as e:
                            st.error("Invalid email address. Please enter a valid email.")
                            return
                        if password_signup != confirm_password:
                            st.error("Passwords do not match. Please try again.")
                        elif not all([email_signup, password_signup, confirm_password, name_signup, company_name, terms_conditions]):
                            st.warning("Please fill in all the fields and agree to the terms and conditions before signing up.")
                        else:
                            if admin_user_exists(company_name):
                                st.error("An admin account already exists for this company.")
                            else:
                                create_new_user({"email": email_signup.lower(), "password": password_signup, "name": name_signup, "role": "admin"}, company_name, is_initial_admin=True)
                                st.success("Signup was successful! You can now log in.")
                                st.session_state.signup_redirect = False  # Reset the signup redirect flag

                            time.sleep(2)
                            st.experimental_rerun()