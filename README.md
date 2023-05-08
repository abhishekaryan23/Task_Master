# Task Management App

A Task Management application built using Streamlit, Python, and MongoDB.

## Installation

1. Clone this repository.
2. Set up a virtual environment and activate it.
3. Install the required packages using `pip install -r requirements.txt`.
4. Create a `.env` file and set the following variables:

```
MONGO_CONNECTION_STRING=<your_mongodb_connection_string>
PASSWORD=<your_mongodb_password>
```
5. Run the app using the command `streamlit run app.py`.

## Features

- User and admin authentication
- Create and manage users
- Create and assign tasks
- Monitor task progress
- Update task status
- Filter tasks by status