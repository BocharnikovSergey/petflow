import os
import json

import firebase_admin
from firebase_admin import credentials


if not firebase_admin._apps:
    firebase_dict = json.loads(
        os.getenv('FIREBASE_CREDENTIALS', '')
    )

    cred = credentials.Certificate(firebase_dict)

    firebase_admin.initialize_app(cred)