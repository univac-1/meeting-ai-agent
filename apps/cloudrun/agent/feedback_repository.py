from config import Config
from utils import get_jst_timestamp

db_client = Config.get_db_client()

def post_feedback(meeting_id, message, detail):
    data = {
        "created_at": get_jst_timestamp(),  # スピーカーを追加
        "message": message,  # メッセージを追加
        "meta": detail,  # AIによる補足情報
    }

    db_client.collection(Config.FIRESTORE_MEETING_COLLECTION).document(
        meeting_id
    ).collection(Config.FIRESTORE_FEEDBACKS_COLLECTION).add(data)

    return meeting_id
