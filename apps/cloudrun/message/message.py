from config import Config
from typing import Optional

from utils import get_jst_timestamp

db_client = Config.get_db_client()


def post_message(meeting_id, speaker, message, meta=None):
    data = {
        "speak_at": get_jst_timestamp(),
        "speaker": speaker,  # スピーカーを追加
        "message": message,  # メッセージを追加
        "meta": meta,  # AIによる補足情報
    }

    db_client.collection(Config.FIRESTORE_MEETING_COLLECTION).document(
        meeting_id
    ).collection(Config.FIRESTORE_COMMENT_COLLECTION).add(data)

    return meeting_id


def get_message_history(meeting_id: str, limit_to_last: Optional[int] = None):
    """
    発言を時系列順（古いものが先）に取得する。

    - `limit_to_last` を指定すると、最新 N 件のみを取得。
    - 指定しない場合は、すべての発言を取得。
    """

    comments_ref = (
        db_client.collection(Config.FIRESTORE_MEETING_COLLECTION)
        .document(meeting_id)
        .collection(Config.FIRESTORE_COMMENT_COLLECTION)
        .order_by("speak_at")
        .limit_to_last(limit_to_last)
    )

    comments = comments_ref.get()

    message_history = []
    for comment in comments:
        data = comment.to_dict()
        # AIの発言以外をフィルタリング
        meta = data.get("meta")
        if meta is None or meta.get("role", "") != "ai":
            message_history.append(data)

    return message_history
