from pymongo import MongoClient
from bson import ObjectId
import sys
import streamlit as st

MONGO_URI = st.secrets['MONGO_URI']

client = MongoClient(MONGO_URI)
db = client.task_management
