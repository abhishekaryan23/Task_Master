# helpers.py
import streamlit as st
from .database import get_db, get_users_collection, ObjectId
import sys
from datetime import datetime
import bcrypt
from .session_state import get_state
from streamlit_lottie import st_lottie
import json
import time


# def get_user_collection(company_name):
#     db = get_db(company_name)
#     return db.users

def get_task_collection(company_name):
    db = get_db(company_name)
    return db.tasks

def find_user_by_email(email):  # Remove company_name parameter
    users = get_users_collection()  # Call the function without arguments
    return users.find_one({"email": email})

# def update_password(email, new_password):  # Remove company_name parameter
#     user = find_user_by_email(email)  # Call without company_name
#     if user:
#         users = get_users_collection()  # Call the function without arguments
#         users.update_one({"email": email}, {"$set": {"password": new_password}})


def login(email, password):
    try:
        users = get_users_collection()
        user = users.find_one({"email": email})
        if user:
            if bcrypt.checkpw(password.encode(), user["password"]):
                return user
            else:
                print("Password check failed")
        else:
            print("User not found")
    except Exception as e:
        print(f"An error occurred: {e}")
    return None

def create_new_user(user_data, company_name, is_initial_admin=False):  
    users = get_users_collection()  

    existing_user = users.find_one({"email": user_data['email'], "company_name": company_name})

    if existing_user:
        raise ValueError("User with this email and company name already exists!")

    hashed_password = bcrypt.hashpw(user_data['password'].encode(), bcrypt.gensalt())
    user_data['password'] = hashed_password
    user_data['company_name'] = company_name
    user_data['is_first_login'] = True  
    user_data['is_initial_admin'] = is_initial_admin  

    users.insert_one(user_data)

def create_task(task_data, company_name):
    tasks = get_task_collection(company_name)

    # If this task depends on another task, add it to that task's dependent_tasks list
    if "depends_on" in task_data and task_data["depends_on"]:
        tasks.update_one(
            {"_id": ObjectId(task_data["depends_on"])},
            {"$push": {"dependent_tasks": task_data["name"]}}
        )

    # The rest of your create_task function...
    task = {
        "name": task_data["name"],
        "description": task_data["description"],
        "assigned_to": task_data["assigned_to"],
        "status": task_data.get("status", "pending"),
        "priority": task_data.get("priority", "Low"),
        "created_at": datetime.utcnow(),
        "depends_on": task_data.get("depends_on"),
        "dependent_tasks": []
    }
    tasks.insert_one(task)

def find_tasks_by_status(status, company_name):
    tasks = get_task_collection(company_name)
    task_list = list(tasks.find({"status": status}))
    return task_list


def update_task_status(task_id, new_status, company_name, comment, minutes_worked, updated_by):
    tasks = get_task_collection(company_name)
    task = tasks.find_one({"_id": ObjectId(task_id)})

    # Check if task is dependent on another task
    if 'depends_on' in task and task['depends_on'] is not None:
        dependent_task = tasks.find_one({"_id": ObjectId(task['depends_on'])})
        if dependent_task['status'] != 'completed':
            assigned_to_user = get_users_collection().find_one({"email": dependent_task['assigned_to']})
            assigned_to_name = assigned_to_user['name'] if assigned_to_user else 'Unknown'
            return f"Cannot complete task. Dependent task '{dependent_task['name']}' is not completed yet. It is assigned to {assigned_to_name}."

    if task:
        tasks.update_one(
            {"_id": ObjectId(task_id)},
            {
                "$set": {"status": new_status},
                "$push": {
                    "status_updates": {
                        "status": new_status,
                        "comment": comment,
                        "timestamp": datetime.utcnow(),
                        "minutes_worked": minutes_worked,
                        "updated_by": updated_by
                    }
                },
            },
        )

    return "Task status updated successfully."

def update_password(email, new_password):
    user = find_user_by_email(email)
    if user:
        users = get_users_collection()
        hashed_new_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
        users.update_one({"email": email}, {"$set": {"password": hashed_new_password}})

# def change_password(email, old_password, new_password, confirm_password):
#     # Check if the new password matches the confirmed password
#     if new_password != confirm_password:
#         return False, "New password and confirmed password do not match."

#     user = find_user_by_email(email)
#     if user and bcrypt.checkpw(old_password.encode(), user["password"]):
#         update_password(email, new_password)
#         return True, "Password updated successfully."
        
#     return False, "The current password is incorrect."

def change_password(email, old_password, new_password, confirm_password, is_first_login=False):
    # If it's the first login, do not check the old password
    if not is_first_login:
        user = find_user_by_email(email)
        if not user or not bcrypt.checkpw(old_password.encode(), user["password"]):
            return False, "The current password is incorrect."
    
    # Check if the new password matches the confirmed password
    if new_password != confirm_password:
        return False, "New password and confirmed password do not match."
    
    update_password(email, new_password)
    
    # Update the is_first_login flag in the database
    users = get_users_collection()
    users.update_one({"email": email}, {"$set": {"is_first_login": False}})
    
    return True, "Password updated successfully."

def admin_user_exists(company_name):
    users = get_users_collection()  # Call the function without arguments
    return users.find_one({"role": "admin", "company_name": company_name}) is not None

def display_password_change_section(email, company_name):
    st.title(f"Welcome to {company_name}")
    st.subheader("Change your password")

    current_password = st.text_input("Current password", type="password")
    new_password = st.text_input("New password", type="password")
    confirm_password = st.text_input("Confirm new password", type="password")

    if st.button("Change password"):
        success, message = change_password(email, current_password, new_password, confirm_password)
        if success:
            st.success(message)
            # Update the session state to reflect the fact that the user is no longer logged in and no longer in their first login
            st.session_state.logged_in = False
            st.session_state.is_first_login = False
            time.sleep(1)
            st.experimental_rerun()  # Rerun the app to redirect the user to the login page
        else:
            st.error(message)

def update_task_priority_based_on_dependencies(company_name):
    tasks = get_task_collection(company_name)
    
    for task in tasks.find():
        if len(task.get("dependent_tasks", [])) >= 2 and task["priority"] != "High":
            tasks.update_one(
                {"_id": task["_id"]},
                {
                    "$set": {"priority": "High"},
                    "$push": {
                        "status_updates": {
                            "status": task["status"],
                            "comment": "2+ tasks dependent on this task, raising priority",
                            "timestamp": datetime.utcnow(),
                            "minutes_worked": 0,
                            "updated_by": "System"
                        }
                    },
                },
            )


@st.cache(allow_output_mutation=True)
def load_lottie_file(path: str):
    with open(path, "r") as f:
        return json.load(f)