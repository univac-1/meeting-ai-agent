from config import Config
from minutes.constants import MinutesFields, ActionPlanFields

from google.cloud import firestore

db_client = Config.get_db_client()


def update_minutes(meeting_id: str, message: str):

    doc_ref = (
        db_client.collection(Config.FIRESTORE_MEETING_COLLECTION)
        .document(meeting_id)
        .collection(Config.FIRESTORE_MINUTES_COLLECTION)
        .document(Config.FIRESTORE_ALL_MINUTES_DOCUMENT)
    )

    if not doc_ref.get().exists:
        print(f"⚠️ ドキュメントが存在しません: {meeting_id}. 新しく作成します。")
        doc_ref.set(
            {
                MinutesFields.AGENDA: [],
                MinutesFields.DECISIONS: [],
                MinutesFields.ACTION_PLAN: [],
            }
        )  # 初期値をセット

    doc_ref.update({MinutesFields.DECISIONS: firestore.ArrayUnion([message])})

    new_action = {
        ActionPlanFields.TASK: message,  # タスクの内容
        ActionPlanFields.ASSIGNED_TO: "未割当",  # 担当者（デフォルト）
        ActionPlanFields.DUE_DATE: "未設定",  # 期限（デフォルト）
    }
    doc_ref.update({MinutesFields.ACTION_PLAN: firestore.ArrayUnion([new_action])})

    print(f"議事録を更新: {message}")
