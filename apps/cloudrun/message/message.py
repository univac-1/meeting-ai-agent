from config import Config
from datetime import datetime
import pytz

MEETING_COLLECTION = "meetings"
COMMENT_COLLECTION = "comments"

db_client = Config.get_db_client()

def post_message(meeting_id, speaker, message):
    tz_japan = pytz.timezone("Asia/Tokyo")
    now = datetime.now(tz_japan).strftime("%Y-%m-%d %H:%M:%S")

    data = {
        "speak_at": now,
        "speaker": speaker,  # スピーカーを追加
        "message": message   # メッセージを追加
    }

    db_client.collection(MEETING_COLLECTION).document(meeting_id).collection(COMMENT_COLLECTION).add(data)

    return meeting_id
