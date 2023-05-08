from .database import db, ObjectId
import sys
from datetime import datetime


def create_new_user(user_data):
    db.users.insert_one(user_data)

def create_task(task_data):
    task = {
        "name": task_data["name"],
        "description": task_data["description"],  # Add this line
        "assigned_to": task_data["assigned_to"],
        "status": task_data["status"],
        "created_at": datetime.utcnow()
    }
    db.tasks.insert_one(task)

def find_tasks_by_status(status):
    return list(db.tasks.find({"status": status}))

def update_task_status(task_id, new_status, comment=None):
    db.tasks.update_one({"_id": ObjectId(task_id)}, {"$set": {"status": new_status, "comment": comment}})
