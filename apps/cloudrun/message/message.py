from config import Config

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


def get_message_history(meeting_id):
    """発言日時が古い方が先に来るように取得"""
    comments_ref = (
        db_client.collection(Config.FIRESTORE_MEETING_COLLECTION)
        .document(meeting_id)
        .collection(Config.FIRESTORE_COMMENT_COLLECTION)
    )
    comments = comments_ref.order_by("speak_at").get()

    message_history = []
    for comment in comments:
        data = comment.to_dict()
        # AIの発言以外をフィルタリング
        meta = data.get("meta")
        if meta is None or meta.get("role", '') != "ai":
            message_history.append(data)

    print(message_history)

    return message_history
