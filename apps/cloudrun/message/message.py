from config import Config
from datetime import datetime
import pytz

MEETING_COLLECTION = "meetings"
# TODO 確認する
COMMENT_COLLECTION = "comments"

db_client = Config.get_db_client()

def post_message(meeting_id, speaker, message, meta=None):
    tz_japan = pytz.timezone("Asia/Tokyo")
    now = datetime.now(tz_japan).strftime("%Y-%m-%d %H:%M:%S")

    data = {
        "speak_at": now,
        "speaker": speaker,  # スピーカーを追加
        "message": message,   # メッセージを追加
        "meta": meta, # AIによる補足情報
    }

    db_client.collection(MEETING_COLLECTION).document(meeting_id).collection(COMMENT_COLLECTION).add(data)

    return meeting_id

def get_message_history(meeting_id):
    """発言日時が古い方が先に来るように取得"""
    comments_ref = db_client.collection(MEETING_COLLECTION).document(meeting_id).collection(COMMENT_COLLECTION)
    comments = comments_ref.order_by("speak_at").get()

    message_history = []
    for comment in comments:
        message_history.append(comment.to_dict())

    return message_history
