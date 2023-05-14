from .database import db, ObjectId
import sys
from datetime import datetime
import bcrypt

def find_user_by_email(email):
    return db.users.find_one({"email": email})

def update_password(email, new_password):
    db.users.update_one({"email": email}, {"$set": {"password": new_password}})

def login(email, password):
    user = find_user_by_email(email)
    if user and bcrypt.checkpw(password.encode(), user["password"]):
        return user
    return None

def create_new_user(user_data):
    hashed_password = bcrypt.hashpw(user_data['password'].encode(), bcrypt.gensalt())
    user_data['password'] = hashed_password
    db.users.insert_one(user_data)

def create_task(task_data):
    task = {
        "name": task_data["name"],
        "description": task_data["description"],  # Add this line
        "assigned_to": task_data["assigned_to"],
        "status": task_data.get("status", "pending"),
        "created_at": datetime.utcnow()
    }
    db.tasks.insert_one(task)


def find_tasks_by_status(status):
    tasks = list(db.tasks.find({"status_updates.status": status}))
    for task in tasks:
        if 'status_updates' in task and task['status_updates']:
            latest_status_update = task['status_updates'][-1]
            task['status'] = latest_status_update['status']
    return tasks

def update_task_status(task_id, new_status, comment=None):
    status_update = {
        "status": new_status,
        "comment": comment,
        "timestamp": datetime.utcnow()
    }
    db.tasks.update_one(
        {"_id": ObjectId(task_id)}, 
        {
            "$push": {"status_updates": status_update}, 
            "$set": {"status": new_status}
        }
    )

def change_password(email, old_password, new_password):
    user = find_user_by_email(email)
    if user and bcrypt.checkpw(old_password.encode(), user["password"]):
        hashed_new_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
        update_password(email, hashed_new_password)
        return True
    return False

def admin_user_exists():
    return db.users.find_one({"role": "admin"}) is not None