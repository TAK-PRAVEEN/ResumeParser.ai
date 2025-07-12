from dotenv import load_dotenv
import os
from pymongo.mongo_client import MongoClient

load_dotenv()

uri = os.getenv("MONGODB_URI")

# Create a new client and connect to the server
client = MongoClient(uri)
db = client["ResumeParser"]