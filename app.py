import streamlit as st
from src.authentication import display_login_page
from src.admin_dashboard import display_admin_dashboard
from src.user_dashboard import display_user_dashboard
from src.session_state import get_state


def run_app():
    st.set_page_config(page_title="Task Management")
    st.sidebar.image("https://raw.githubusercontent.com/abhishekaryan23/Task_Master/master/logo.png")
    st.title("Task Master")

    # Initialize session state
    st.session_state = get_state(logged_in=False, user=None)

    if not st.session_state.logged_in:
        display_login_page()
    else:
        if st.session_state.user["role"] == "admin":
            display_admin_dashboard()
        elif st.session_state.user["role"] == "user":
            display_user_dashboard(st.session_state.user["email"])


if __name__ == "__main__":
    run_app()

