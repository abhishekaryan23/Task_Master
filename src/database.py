from pymongo import MongoClient
from bson import ObjectId
import sys
import streamlit as st
import toml

# Load the contents of the config.toml file
config = toml.load('config.toml')

# Access the MongoDB URI from the loaded config
MONGO_URI = config['mongodb']['uri']

# if you want to host your app on streamlit share uncomment below line and comment the above 2 lines.
# MONGO_URI = st.secrets['MONGO_URI']

client = MongoClient(MONGO_URI)
db = client.task_management