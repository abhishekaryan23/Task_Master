import streamlit as st
from .database import get_users_collection
from .helpers import create_new_user, create_task, find_tasks_by_status, update_task_status, login, change_password, admin_user_exists, get_task_collection, load_lottie_file, update_task_priority_based_on_dependencies
from .session_state import SessionState, get_state
from datetime import datetime
from pymongo import DESCENDING
# from .authentication import display_password_change_section
from .tasks import display_task
from streamlit_lottie import st_lottie
import json
import time
from email_validator import validate_email, EmailNotValidError
import plotly.express as px
from collections import Counter
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import mplcursors

def display_admin_dashboard(name):
    st.sidebar.header("Admin Panel")
    st.sidebar.write(f"Welcome, {name}!")

    admin_options = {
        "My Tasks": "📋",  
        "Create Task": "➕", 
        "Monitor Tasks": "🔍",
        "User Management": "👥",
        "Profile": "👤",
        "Task Statistics": "📊"
    }

    state = get_state()

    if 'selected_option' not in state:
        state['selected_option'] = 'My Tasks'

    for option, emoji in admin_options.items():
        if st.sidebar.button(f"{emoji} {option}"):
            state['selected_option'] = option

    # st.sidebar.write(f"You selected: {state['selected_option']}")

    selected_option = state['selected_option']

    if selected_option == "My Tasks":
        st.subheader("My Tasks")
        hide_completed_tasks = st.checkbox("Hide completed tasks", key="admin_hide_completed", value=True)
        tasks = list(get_task_collection(st.session_state.company_name).find({"assigned_to": st.session_state.user["email"]}))
        
        # Check if there are any tasks assigned to the user
        if len(tasks) == 0:
            st.info("No tasks assigned to you.")
        else:
            for idx, task in enumerate(tasks):
                if not (hide_completed_tasks and task["status"] == "completed"):
                    display_task(task, st.session_state.user["email"], st.session_state.company_name, is_admin=True, allow_status_change=True, task_index=idx)

    elif selected_option == "Create Task":
        st.subheader("Create New Task")

        with st.form(key='create_task_form', clear_on_submit=True):
            task_name = st.text_input("Task Name", "")
            task_description = st.text_area("Task Description", "")
            users = list(get_users_collection().find({"company_name": st.session_state.company_name}))
            user_mapping = {f"{user['name']} ({user['email']})": user['email'] for user in users}
            user_keys = list(user_mapping.keys())
            selected_user_key = st.selectbox("Assign To", [f"{st.session_state.user['name']} ({st.session_state.user['email']})"] + user_keys)
            assign_to = user_mapping.get(selected_user_key, st.session_state.user["email"])

            # Task priority field
            task_priorities = ["High", "Moderate", "Low"]
            task_priority = st.selectbox("Task Priority", task_priorities)

            # Depends on field
            tasks = list(get_task_collection(st.session_state.company_name).find({"status": {"$in": ["pending", "in progress"]}}))
            task_mapping = {task['name']: task['_id'] for task in tasks}
            task_keys = list(task_mapping.keys())
            selected_task_key = st.selectbox("Depends On", ["None"] + task_keys)
            depends_on = task_mapping.get(selected_task_key)

            create_task_btn = st.form_submit_button("Create Task")

            if create_task_btn:
                create_task({
                    "name": task_name, 
                    "description": task_description, 
                    "assigned_to": assign_to, 
                    "status": "pending", 
                    "priority": task_priority, 
                    "depends_on": depends_on  # Add this line
                }, st.session_state.company_name)
                update_task_priority_based_on_dependencies(st.session_state.company_name)  # Add this line
                st.success("Task created successfully!")
                time.sleep(2)
                st.experimental_rerun()

    elif selected_option == "Monitor Tasks":
        st.subheader("Monitor Tasks")
        monitor_options = [
            "Monitor all tasks",
            "Fetch Tasks by Status",
            "Fetch Tasks by User",
            "Search Tasks by Name",
            "Fetch Tasks by Priority",  # Add this line
        ]
        selected_monitor_option = st.selectbox("Select an option", monitor_options)

        if selected_monitor_option == "Monitor all tasks":
            col1, col2 = st.columns(2)
            with col1:
                hide_completed_tasks = st.checkbox("Hide completed tasks", value=True)
            with col2:
                with st.container():
                    sort_by_days_passed = st.checkbox("Sort tasks by days passed", value=False, key="sort_by_days_passed")

            tasks = get_task_collection(st.session_state.company_name).find().sort("created_at", DESCENDING if sort_by_days_passed else None)

            if hide_completed_tasks:
                tasks = [task for task in tasks if "status" in task and task["status"] != "completed"]

            if not tasks:
                st.info("No tasks found.")
            else:
                st.write("---")
                for idx, task in enumerate(tasks):
                    display_task(task, st.session_state.user["email"], st.session_state.company_name, is_admin=True, allow_status_change=False, task_index=idx)
                    st.write("---") 

        elif selected_monitor_option == "Fetch Tasks by Status":
            status_mapping = {"Pending": "pending", "In Progress": "in progress", "Completed": "completed", "Cancelled":"cancelled"}
            status_keys = list(status_mapping.keys())
            selected_status_key = st.selectbox("Select Status", status_keys)
            status = status_mapping[selected_status_key]

            tasks = find_tasks_by_status(status, st.session_state.company_name)
            
            if not tasks:
                st.info("No tasks found with the selected status.")
            else:
                st.write("---")
                for idx, task in enumerate(tasks):
                    display_task(task, st.session_state.user["email"], st.session_state.company_name, is_admin=True, allow_status_change=False, task_index=idx)
                    st.write("---") 

        elif selected_monitor_option == "Fetch Tasks by Priority":
            priority_mapping = {"High": "High", "Moderate": "Moderate", "Low": "Low"}
            priority_keys = list(priority_mapping.keys())
            selected_priority_key = st.selectbox("Select Priority", priority_keys)
            priority = priority_mapping[selected_priority_key]

            task_count = get_task_collection(st.session_state.company_name).count_documents({"priority": priority})

            if task_count == 0:
                st.info("No tasks found with the selected priority.")
            else:
                st.write("---")
                tasks = get_task_collection(st.session_state.company_name).find({"priority": priority})
                for idx, task in enumerate(tasks):
                    display_task(task, st.session_state.user["email"], st.session_state.company_name, is_admin=True, allow_status_change=False, task_index=idx)
                    st.write("---") 

        elif selected_monitor_option == "Fetch Tasks by User":
            users = list(get_users_collection().find({"company_name": st.session_state.company_name}))
            user_mapping = {f"{user['name']} ({user['email']})": user['email'] for user in users}
            user_keys = list(user_mapping.keys())
            selected_user_key = st.selectbox("Select User", user_keys)
            user_email = user_mapping[selected_user_key]

            task_count = get_task_collection(st.session_state.company_name).count_documents({"assigned_to": user_email})

            if task_count == 0:
                st.info("No tasks found for the selected user.")
            else:
                tasks = get_task_collection(st.session_state.company_name).find({"assigned_to": user_email})
                st.write("---")
                for idx, task in enumerate(tasks):
                    display_task(task, st.session_state.user["email"], st.session_state.company_name, is_admin=True, allow_status_change=False, task_index=idx)
                    st.write("---") 

        elif selected_monitor_option == "Search Tasks by Name":
            st.subheader("Search Tasks by Name")
            search_query = st.text_input("Enter task name to search")
            search_btn = st.button("Search")
            if search_btn and search_query:
                tasks = get_task_collection(st.session_state.company_name).find({"name": {"$regex": search_query, "$options": "i"}})
                task_count = get_task_collection(st.session_state.company_name).count_documents({"name": {"$regex": search_query, "$options": "i"}})

                if task_count == 0:
                    st.info("No tasks found matching your search query.")
                else:
                    st.write("---")
                    for idx, task in enumerate(tasks):
                        display_task(task, st.session_state.user["email"], st.session_state.company_name, is_admin=True, allow_status_change=False, task_index=idx)
                        st.write("---") 
    elif selected_option == "User Management":
        st.subheader("User Management")

        # Create New User button
        create_user_btn = st.button('Create New User \U0001F464')
        if create_user_btn:
            st.session_state.show_create_user_form = not st.session_state.show_create_user_form  # Flip the boolean flag

        # Display user creation form only when the session state flag is True
        if st.session_state.show_create_user_form:
            with st.form(key='create_user_form', clear_on_submit=True):
                new_name = st.text_input("New User Name", "")
                new_email = st.text_input("New User Email", "")
                new_password = st.text_input("New User Password", type="password", value="password@123")
                confirm_password = st.text_input("Confirm Password", type="password", value="password@123")
                role_mapping = {"Admin": "admin", "User": "user"}
                role_keys = list(role_mapping.keys())  # ["Admin", "User"]
                selected_role_key = st.selectbox("Role", role_keys)
                role = role_mapping[selected_role_key]

                create_user_submit_btn = st.form_submit_button("Submit")

                if create_user_submit_btn:
                    try:
                        validated_email = validate_email(new_email)
                    except EmailNotValidError as e:
                        st.error("Invalid email address. Please enter a valid email.")
                        return
                    if new_password == confirm_password:
                        try:
                            create_new_user({"name": new_name, "email": new_email.lower(), "password": new_password, "role": role}, st.session_state.company_name)
                            st.success("User created successfully!")
                            time.sleep(2)
                            st.experimental_rerun()
                        except ValueError as e:
                            st.error(str(e))
                    else:
                        st.error("Passwords do not match. Please try again.")

        # User Management table
        users = list(get_users_collection().find({"company_name": st.session_state.company_name}))

        # Create column headers
        col1, col2, col3, col4 = st.columns(4)
        col1.subheader("Name")
        col2.subheader("Email")
        col3.subheader("Role")
        col4.subheader("Actions")

        # Check if there are any users
        if len(users) == 0:
            st.info("No users in this company.")
        else:
            for idx, user in enumerate(users):

                if user["email"] != st.session_state.user["email"]:  # Admin cannot delete themselves
                    st.write("---") 
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.write(user["name"])
                    with col2:
                        st.write(user["email"])
                    with col3:
                        st.write(user["role"])
                    with col4:
                        # Split the name by spaces and pick the first name
                        first_name = user["name"].split(' ')[0]
                        delete_user_btn = st.button(f"Delete {first_name}")
                        if delete_user_btn:
                            get_users_collection().delete_one({"email": user["email"]})
                            st.success(f"User {user['name']} deleted successfully!")
                            time.sleep(1)
                            st.experimental_rerun()



    elif selected_option == "Profile":
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
            st.write(f"**Project Name:** {st.session_state.company_name}")
            st.write(f"**Role:** {st.session_state.user['role'].capitalize()}")

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

    elif selected_option == "Task Statistics":
        st.subheader("Task Statistics")

        # Get all tasks
        tasks = list(get_task_collection(st.session_state.company_name).find())
        
        # Create columns
        col1, col2 = st.columns(2)
        
        # Task Status Pie chart
        task_status = [task['status'] for task in tasks]

        # Only include statuses that exist
        all_statuses = ['pending', 'in progress', 'completed', 'cancelled']
        task_status = [status for status in task_status if status in all_statuses]

        df_status = pd.DataFrame(task_status, columns=['status'])
        fig = px.pie(df_status, names='status', title='Task Status Distribution', color = 'status',
                    color_discrete_map={'pending':'#FA6C5C', 'in progress':'#6C5CFA', 'completed':'#36F57F', 'cancelled':'#A2AD9C'})
        col1.plotly_chart(fig, config={'displayModeBar': False})

        # Task Priority Histogram
        task_priorities = [task['priority'] for task in tasks]
        df_priority = pd.DataFrame(task_priorities, columns=['priority'])
        df_priority['count'] = 1  # adding a count column
        df_priority_grouped = df_priority.groupby('priority').count().reset_index()  # grouping by priority and counting

        fig = px.bar(df_priority_grouped, x='priority', y='count', color='priority', title='Task Priority Distribution', 
                    color_discrete_map={'High':'#F62817', 'Moderate':'#157DEC', 'Low':'#36F57F'})
        col2.plotly_chart(fig, config={'displayModeBar': False})


        
        # User-specific Task Distribution
        user_task_counts = Counter(task['assigned_to'] for task in tasks)
        users = list(user_task_counts.keys())
        user_task_nums = list(user_task_counts.values())
        df_user = pd.DataFrame(list(zip(users, user_task_nums)), columns=['user', 'task_count'])
        fig = px.bar(df_user, x='user', y='task_count', color='user', title='User-specific Task Distribution')
        col1.plotly_chart(fig, config={'displayModeBar': False})

        # Task Distribution over Time Line Chart
        task_creation_times = [task['created_at'] for task in tasks]
        task_creation_times.sort()
        task_counts_over_time = list(range(1, len(task_creation_times) + 1))
        fig = px.line(x=task_creation_times, y=task_counts_over_time, title='Task Distribution Over Time')
        col2.plotly_chart(fig, config={'displayModeBar': False})
        

        # Create a directed graph
        G = nx.DiGraph()

        # Add a node for each task
        for task in tasks:
            G.add_node(task["name"])

        # Add an edge for each dependency
        for task in tasks:
            for dependent_task in task["dependent_tasks"]:
                G.add_edge(dependent_task, task["name"])  # Add an edge from the dependent task to the task

        with st.expander("See Task dependency graph"):
            # Draw the graph
            fig, ax = plt.subplots(figsize=(10, 5))  # Create a figure and an axes.
            # Compute a layout position for the graph
            pos = nx.spring_layout(G)
            # Draw the graph
            nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=1500, edge_cmap=plt.cm.Blues, font_size=10, ax=ax)
            # Display the figure in Streamlit
            st.pyplot(fig)

    st.sidebar.write("")  # Add some space before the logout button
    st.sidebar.write("")  # Add more space (repeat as needed)
    st.sidebar.write("")
    logout_btn = st.sidebar.button("Logout", key="admin_logout")
    if logout_btn:
        st.session_state.clear()  # Clear all items from the session state
        # Re-initialize necessary attributes
        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.page = "Login"  # or any default page you want after logout
        st.experimental_rerun()
