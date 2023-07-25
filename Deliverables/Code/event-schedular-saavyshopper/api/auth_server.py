from firebase_admin import credentials, firestore, initialize_app
import os
from dotenv import load_dotenv
load_dotenv()

cred = credentials.Certificate(os.environ.get("firebase_token"))
default_app = initialize_app(cred)
db = firestore.client()