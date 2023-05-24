import streamlit as st
from .database import get_users_collection
from .helpers import create_new_user, create_task, find_tasks_by_status, update_task_status, login, change_password, admin_user_exists, get_task_collection
from .session_state import SessionState, get_state
from datetime import datetime
from pymongo import DESCENDING
import pytz
from bson import ObjectId

def truncate_text(text, max_length):
    """Truncate text and append '...' if it exceeds the max_length."""
    if len(text) > max_length:
        return text[:max_length] + "..."
    else:
        return text


def display_task(task, email=None, company_name=None, is_admin=False, allow_status_change=True, task_index=0):
    status_color = {
        "pending": "red",
        "in progress": "orange",
        "completed": "green",
        "cancelled": "black"
    }
    priority_color = {
        "High": "red",
        "Moderate": "orange",
        "Low": "green"
    }
    col1, col2, col3, col4, col5, col6, col7 = st.columns([4, 3, 2, 2, 2, 1, 1])
    with col1:
        truncated_name = truncate_text(task['name'], 30)  # Adjust 30 to your desired max length
        st.markdown(f"**Task**: {truncated_name}")
    with col2:
        st.markdown(f"**Assigned to**: {task['assigned_to']}")
    with col3:
        st.markdown(f'**Status**: <p style="color:{status_color[task["status"]]}">{task["status"]}</p>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'**Priority**: <p style="color:{priority_color[task["priority"]]}">{task["priority"]}</p>', unsafe_allow_html=True)
    days_passed = (datetime.utcnow() - task['created_at']).days
    with col5:
        st.markdown(f"**Days passed**: {days_passed}")
    with col6:
        st.empty()  # You can put anything else here or leave it empty
    if email:
        unique_key = f"{task['_id']}-{email}-{task_index:05d}"
        with col7:
            view_update_btn = st.button("View/Update", key=f"view-update-{unique_key}")
        if view_update_btn:
            # Store the selected task details in session state
            get_state().selected_task_id = str(task['_id'])
            get_state().company_name = company_name
            # Navigate to the task details page
            get_state().page = "Task Details"                
            st.experimental_rerun()


def display_task_details(email=None):
    st.subheader("Task Details")

    back_to_dashboard = st.button('Back to My Tasks')
    if back_to_dashboard:
        get_state().page = "Dashboard"
        st.experimental_rerun()

    # Get the selected task details from the database
    task = get_task_collection(st.session_state.company_name).find_one({"_id": ObjectId(st.session_state.selected_task_id)})
    truncated_name = truncate_text(task['name'], 30)

    # Fetch user data
    user = get_users_collection().find_one({"email": email})
    first_name = user['name'].split(' ')[0]
    updated_by = f"{first_name} ({email})"

    with st.container():
        st.write('---')  # This will draw a horizontal line
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Task:**")
            st.markdown("**Assigned to:**")
            st.markdown("**Description:**")
            st.markdown("")
            st.markdown("**Status:**")
            st.markdown("**Priority:**")
            st.markdown("")
            st.markdown("**Dependent Tasks:**")
        with col2:
            st.markdown(f"{task['name']}")
            st.markdown(f"{task['assigned_to']}")
            description_expander = st.expander("Description", expanded=False)
            description_expander.markdown(f'<div style="height:250px; overflow:auto;border:1px solid black;padding:10px;">{task["description"]}</div>', unsafe_allow_html=True)
            st.markdown(f"{task['status'].capitalize()}")
            st.markdown(f"{task['priority']}")
            dependent_tasks_expander = st.expander("Dependent Tasks", expanded=False)
            if task["dependent_tasks"]:
                dependent_tasks = get_task_collection(st.session_state.company_name).find({"name": {"$in": task["dependent_tasks"]}})
                dependent_tasks_info = [(t["name"], t["assigned_to"]) for t in dependent_tasks]
                dependent_tasks_expander.markdown('<br>'.join(f'{name} (Assigned to: {assigned_to})' for name, assigned_to in dependent_tasks_info), unsafe_allow_html=True)
            else:
                dependent_tasks_expander.markdown('No dependent tasks.')
        st.write('---')
        
        if email and task["status"] not in ["completed", "cancelled"]:
            unique_key = f"{task['_id']}-{email}"
            with st.form(key=f"update_form-{unique_key}", clear_on_submit=True):
                row1_col1, row1_col2 = st.columns([2,2])
                with row1_col1:
                    status_options = ["Pending", "In Progress", "Completed", "Cancelled"]
                    selected_status = st.selectbox(f"Update status for {truncated_name}", status_options, key=f"status-{unique_key}")
                    new_status = selected_status.lower()
                with row1_col2:
                    minutes_worked = st.number_input("Minutes worked", min_value=0, step=1, format="%i", key=f"minutes-{unique_key}")  # Add this line
                comment = st.text_area(f"Add comment for {truncated_name}:",key=f"comment-{unique_key}")
                update_task_btn = st.form_submit_button("Update")
            
            if update_task_btn:
                if not comment.strip() and minutes_worked != 0:
                    st.error(f"Please provide a reason for updating the minutes worked.")
                else:
                    update_task_status(str(task["_id"]), new_status, st.session_state.company_name, comment.strip() if comment else None, minutes_worked, updated_by)  # Pass hours_worked and email to the function
                    if new_status != task["status"]:
                        task["status"] = new_status
                    st.success("Task updated successfully!")
        elif task["status"] in ["completed", "cancelled"]:
            st.info("This task is already completed or cancelled and cannot be updated.")

    # Show the status updates
    for status_update in task.get('status_updates', []):
        with st.container():
            # st.write('---')  # This will draw a horizontal line
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"**Comment**: {status_update['comment']}")
            with col2:
                st.markdown(f"**Minutes Worked**: {status_update['minutes_worked']}")
            with col3:
                st.markdown(f"**Time (IST)**: {status_update['timestamp'].astimezone(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')}")
            with col4:
                st.markdown(f"**Updated By**: {status_update['updated_by']}")
            st.write('---')







