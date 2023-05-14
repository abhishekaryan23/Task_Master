import streamlit as st
from .database import db
from .helpers import create_new_user, create_task, find_tasks_by_status, update_task_status, login, change_password, admin_user_exists
from .session_state import SessionState
from datetime import datetime
from pymongo import DESCENDING
import pytz




def display_task(task, email=None, is_admin=False, allow_status_change=True, task_index=0):
    status_color = {
        "pending": "red",
        "in progress": "orange",
        "completed": "green"
    }
    col1, col2, col3, col4, col5 = st.columns([3, 3, 5, 2, 1])
    with col1:
        st.markdown(f"**Task**: {task['name']}")
    with col2:
        st.markdown(f"**Assigned to**: {task['assigned_to']}")
    with col3:
        st.markdown(f"**Description**: {task['description']}")
    with col4:
        st.markdown(f'**Status**: <p style="color:{status_color[task["status"]]}">{task["status"]}</p>', unsafe_allow_html=True)

    days_passed = (datetime.utcnow() - task['created_at']).days
    with col5:
        st.markdown(f"**Days passed**: {days_passed}")

    if 'status_updates' in task and st.button(f'View Comments for {task["name"]}'):
        comments = task['status_updates']  # assuming status_updates is a list of dictionaries where each dictionary has 'comment' and 'timestamp' keys
        for comment in comments:
            timestamp_utc = comment['timestamp']
            timestamp_ist = timestamp_utc.replace(tzinfo=pytz.UTC).astimezone(pytz.timezone('Asia/Kolkata'))
            st.write(f"**Comment**: {comment['comment']} - Time: {timestamp_ist.strftime('%Y-%m-%d %H:%M:%S')} IST")

    if email:
        if task["status"] != "completed" and allow_status_change:
            unique_key = f"{task['_id']}-{email}-{task_index:05d}"
            new_status = st.selectbox(f"Update status for {task['name']}", ["pending", "in progress", "completed"], key=f"status-{unique_key}")

            if new_status != task["status"]:
                comment = st.text_area(f"Please provide a reason for moving the task to {new_status}:", key=f"comment-{unique_key}")

                update_task_btn = st.button("Update Task Status", key=f"update-{unique_key}")

                if update_task_btn:
                    if not comment.strip():
                        st.error(f"Please provide a reason for moving the task to {new_status}.")
                    else:
                        update_task_status(str(task["_id"]), new_status, comment.strip() if comment else None)
                        task["status"] = new_status  # Update the task object
                        st.success("Task status updated successfully!")
    elif task["status"] == "completed" and not allow_status_change:
        st.info("This task is already completed and cannot be updated.")