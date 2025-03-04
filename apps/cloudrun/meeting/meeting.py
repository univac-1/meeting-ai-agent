import uuid
from typing import List, Optional
from typing_extensions import TypedDict
from config import Config


# アジェンダ項目の型定義
class AgendaItem(TypedDict):
    topic: str
    duration: int


db_client = Config.get_db_client()


def generate_meeting_id():
    uuid_int = uuid.uuid4().int  # UUIDを整数に変換
    base36 = ""
    chars = "0123456789abcdefghijklmnopqrstuvwxyz"  # 小文字の36進数

    # 36 進数に変換（8 桁分を取得）
    for _ in range(8):
        base36 = chars[uuid_int % 36] + base36
        uuid_int //= 36

    return base36


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
    # 会議IDの生成
    meeting_id = generate_meeting_id()

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
