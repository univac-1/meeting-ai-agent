import uuid
from config import Config

FIRESTORE_MEETING_COLLECTION = Config.FIRESTORE_MEETING_COLLECTION

db_client = Config.get_db_client()

def create_meeting(
    meeting_name, participants, agenda, start_date, start_time, end_time, meeting_purpose
):
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

    db_client.collection(FIRESTORE_MEETING_COLLECTION).document(meeting_id).set(data)

    return meeting_id
