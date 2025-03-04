import os
from dotenv import load_dotenv
import google.cloud.firestore
from threading import Lock


class Config:
    """環境変数やアプリ共通設定など"""

    load_dotenv()

    FIRESTORE_MEETING_COLLECTION = "meetings"
    FIRESTORE_COMMENT_COLLECTION = "comments"
    FIRESTORE_MINUTES_COLLECTION = "minutes"
    FIRESTORE_ALL_MINUTES_DOCUMENT = "all_minutes"
    FIRESTORE_FEEDBACKS_COLLECTION = "feedbacks"

    # GCPのPROJECT_ID
    PROJECT_ID = os.getenv("PROJECT_ID")

    dbname = "ai-agent-cfs"
    _db_client = None
    _db_client_lock = Lock()

    @classmethod
    def get_db_client(cls):
        with cls._db_client_lock:
            if cls._db_client is None:
                cls._db_client = google.cloud.firestore.Client(database=cls.dbname)
        return cls._db_client

    @classmethod
    def get_ai_facilitator_name(cls):
        return "AIファシリテータ"
