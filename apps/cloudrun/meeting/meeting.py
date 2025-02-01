import uuid
from typing import List, Optional
from typing_extensions import TypedDict
from config import Config


# アジェンダ項目の型定義
class AgendaItem(TypedDict):
    topic: str
    duration: int


# 会議更新データの型定義
class MeetingUpdateFields(TypedDict, total=False):
    meeting_name: Optional[str]
    meeting_purpose: Optional[str]
    start_date: Optional[str]  # YYYY-MM-DD
    start_time: Optional[str]  # HH:MM
    end_time: Optional[str]  # HH:MM
    participants: Optional[List[str]]
    agenda: Optional[List[AgendaItem]]


db_client = Config.get_db_client()


def create_meeting(
    meeting_name: str,
    participants: List[str],
    agenda: List[AgendaItem],
    start_date: str,
    start_time: str,
    end_time: str,
    meeting_purpose: str,
) -> str:
    """
    会議情報をFirestoreに保存し、ユニークな会議IDを生成して返す。

    Args:
        meeting_name (str): 会議名
        participants (list): 参加者のリスト
        agenda (list): アジェンダのリスト (各項目は辞書形式)
        start_date (str): 会議開始日 (YYYY-MM-DD)
        start_time (str): 会議開始時刻 (HH:MM)
        end_time (str): 会議終了時刻 (HH:MM)
        meeting_purpose (str): 会議の目的

    Returns:
        str: 生成されたユニークな会議ID
    """
    # UUIDの生成
    meeting_id = str(uuid.uuid4())

    # 保存するデータの構築
    data = {
        "meeting_name": meeting_name,
        "meeting_purpose": meeting_purpose,
        "start_date": start_date,
        "start_time": start_time,
        "end_time": end_time,
        "participants": participants,
        "agenda": agenda,
    }

    db_client.collection(Config.FIRESTORE_MEETING_COLLECTION).document(meeting_id).set(
        data
    )

    return meeting_id


def update_meeting(meeting_id: str, update_data: MeetingUpdateFields) -> bool:
    """
    指定された会議IDの情報を更新する。

    Args:
        meeting_id (str): 更新対象の会議ID
        update_data (MeetingUpdateFields): 更新するデータ
            - meeting_name: 会議名（任意）
            - meeting_purpose: 会議の目的（任意）
            - start_date: 会議開始日 YYYY-MM-DD（任意）
            - start_time: 会議開始時刻 HH:MM（任意）
            - end_time: 会議終了時刻 HH:MM（任意）
            - participants: 参加者のリスト（任意）
            - agenda: アジェンダのリスト（任意）

    Returns:
        bool: 更新が成功したかどうか
    """
    try:
        # 会議の存在確認
        doc_ref = db_client.collection(Config.FIRESTORE_MEETING_COLLECTION).document(
            meeting_id
        )
        if not doc_ref.get().exists:
            return False

        # データの更新
        doc_ref.update(update_data)
        return True

    except Exception as e:
        print(f"Error updating meeting: {e}")
        return False
