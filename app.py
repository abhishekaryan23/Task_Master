import streamlit as st
from src.authentication import display_login_page
from src.admin_dashboard import display_admin_dashboard  # you might need to update this
from src.user_dashboard import display_user_dashboard
from src.session_state import get_state
from src.helpers import display_password_change_section
from src.tasks import display_task_details  # Add this import at the top of your file

def run_app():
    st.set_page_config(page_title="Task Management", layout="wide")
    st.sidebar.image("https://raw.githubusercontent.com/abhishekaryan23/Task_Master/master/logo.png")
    st.title("Task Master")

    st.session_state = get_state()

    # Initialize the new session state variable
    if 'show_create_user_form' not in st.session_state:
        st.session_state.show_create_user_form = False

    if not st.session_state.logged_in:
        display_login_page()
    else:
        if st.session_state.is_first_login and (st.session_state.user is not None and not st.session_state.user.get('is_initial_admin', False)):  
            display_password_change_section(st.session_state.user["email"], st.session_state.company_name)  # Redirect to password change function
        else:
            if st.session_state.user["role"] == "admin":
                if st.session_state.page == "Task Details":
                    display_task_details(st.session_state.user["email"])
                else:
                    display_admin_dashboard(st.session_state.user["name"])  # add st.session_state as a parameter
            elif st.session_state.user["role"] == "user":
                if st.session_state.page == "Task Details":
                    display_task_details(st.session_state.user["email"])
                else:
                    display_user_dashboard(st.session_state.user["name"])

if __name__ == "__main__":
    run_app()
