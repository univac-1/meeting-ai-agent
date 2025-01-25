import uuid
from config import Config

MEETING_COLLECTION = "meetings"
INFORMATION_DOCUMENT = "information"

db_client = Config.get_db_client()

def create_meeting(meeting_name, participants, agenda):  # 引数を追加
    # UUIDの生成
    meeting_id = str(uuid.uuid4())

    data = {
        "meeting_id": meeting_id,
        "meeting_name": meeting_name,  # 会議名を追加
        "participants": participants,     # 参加者のリストを追加
        "agenda": agenda                  # アジェンダのリストを追加
    }

    db_client.collection(f"{MEETING_COLLECTION}/{meeting_id}").document(INFORMATION_DOCUMENT).add(data)

    return meeting_id
