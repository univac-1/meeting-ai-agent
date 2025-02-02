from typing import Optional, Tuple
from datetime import datetime
import pytz
from config import Config
from message.message import get_message_history
from models import InterventionStatus, InterventionRequest, MeetingInput
from .intervention_check_agent import should_intervene
import os
FIRESTORE_MEETING_COLLECTION = Config.FIRESTORE_MEETING_COLLECTION

AGENT_INTERVENTION_SPAN_SECONDS = int(os.getenv("AGENT_INTERVENTION_SPAN_SECONDS", 10))


def _create_intervention_request(meeting_id: str, reason: str) -> bool:
    """介入リクエストを作成する"""
    db = Config.get_db_client()
    doc_ref = db.collection(FIRESTORE_MEETING_COLLECTION).document(meeting_id)
    
    tz_japan = pytz.timezone("Asia/Tokyo")
    now = datetime.now(tz_japan).strftime("%Y-%m-%d %H:%M:%S")
    
    intervention_request = {
        "status": InterventionStatus.PENDING,
        "reason": reason,
        "created_at": now,
        "updated_at": now
    }
    
    doc_ref.update({
        "intervention_request": intervention_request
    })

def _get_intervention_request(meeting_id: str) -> Optional[dict]:
    """介入リクエストを取得する"""
    db = Config.get_db_client()
    doc_ref = db.collection(FIRESTORE_MEETING_COLLECTION).document(meeting_id)
    doc = doc_ref.get()
    
    if not doc.exists:
        return None
    
    meeting_data = doc.to_dict()
    return meeting_data.get("intervention_request")

def _get_meeting_data_for_intervention(meeting_id: str) -> Optional[MeetingInput]:
    """介入のための会議データを取得する"""
    db = Config.get_db_client()
    doc_ref = db.collection(FIRESTORE_MEETING_COLLECTION).document(meeting_id)
    doc = doc_ref.get()
    
    if not doc.exists:
        return None
    
    meeting_data = doc.to_dict()
    message_history = get_message_history(meeting_id)
    if not message_history:
        return None
    
    # 介入リクエストの取得
    intervention_data = meeting_data.get("intervention_request")
    intervention_request = InterventionRequest(**intervention_data) if intervention_data else None
    
    return MeetingInput(
        purpose=meeting_data.get("meeting_purpose"),
        agenda=meeting_data.get("agenda"),
        participants=meeting_data.get("participants", []),
        comment_history=message_history if isinstance(message_history, list) else [message_history],
        start_at=f"{meeting_data['start_date']} {meeting_data['start_time']}:00",
        end_at=f"{meeting_data['start_date']} {meeting_data['end_time']}:00",
        intervention_request=intervention_request
    )

def _check_if_intervention_needed(meeting_id: str) -> Tuple[bool, Optional[str]]:
    """介入が必要かどうかを判断する"""
    intervention_request = _get_intervention_request(meeting_id)
    
    # 既に介入リクエストが存在し、かつ完了していない場合は新たな介入は不要
    if intervention_request is not None:
        if intervention_request.get("status") == InterventionStatus.PENDING:
            return False, None
        if intervention_request.get("status") == InterventionStatus.COMPLETED:
            # 文字列形式の日時を比較
            tz_japan = pytz.timezone("Asia/Tokyo")
            now = datetime.now(tz_japan).strftime("%Y-%m-%d %H:%M:%S")
            last_update = intervention_request.get("updated_at")
            
            time_diff = (
                datetime.strptime(now, "%Y-%m-%d %H:%M:%S") - 
                datetime.strptime(last_update, "%Y-%m-%d %H:%M:%S")
            ).total_seconds()
            
            if time_diff < AGENT_INTERVENTION_SPAN_SECONDS:
                return False, None

    # 会議データを取得
    meeting_input = _get_meeting_data_for_intervention(meeting_id)
    if not meeting_input:
        return False, None
    
    # LLMを使用して介入の必要性を判断
    return should_intervene(meeting_input)

def request_intervention(meeting_id: str) -> bool:
    """メッセージに対する介入処理を行う"""
    should_intervene_flag, reason = _check_if_intervention_needed(meeting_id)
    print(should_intervene_flag, reason)
    
    if not should_intervene_flag:
        return False
    
    # 介入リクエストを作成
    _create_intervention_request(meeting_id, reason)
    
    return True 