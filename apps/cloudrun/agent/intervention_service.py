from typing import Optional, Dict
from datetime import datetime
from agent.feedback_agent import process_meeting_feedback, MeetingInput
from config import Config
from message.message import get_message_history
from .intervention_request_service import InterventionStatus, InterventionRequest
from message.message import post_message
import json
import pytz

FIRESTORE_MEETING_COLLECTION = Config.FIRESTORE_MEETING_COLLECTION

def _complete_intervention(meeting_id: str) -> bool:
    """介入リクエストを完了状態に更新する"""
    db = Config.get_db_client()
    doc_ref = db.collection(FIRESTORE_MEETING_COLLECTION).document(meeting_id)

    tz_japan = pytz.timezone("Asia/Tokyo")
    now = datetime.now(tz_japan).strftime("%Y-%m-%d %H:%M:%S")
    
    doc_ref.update({
        "intervention_request.status": InterventionStatus.COMPLETED,
        "intervention_request.updated_at": now
    })
    return True

#TODO main.pyのコメント生成と整合性を取る
def generate_intervention_message(meeting_id: str) -> Optional[str]:
    """介入メッセージを生成する"""
    feedback = _generate_feedback(meeting_id)
    
    # 介入リクエストを完了状態に更新
    _complete_intervention(meeting_id)
    
    return feedback.message

FIRESTORE_MEETING_COLLECTION = Config.FIRESTORE_MEETING_COLLECTION

def _generate_feedback(meeting_id: str) -> Optional[Dict]:
    """
    指定された会議IDに対するエージェントのフィードバックを生成します。
    
    Args:
        meeting_id (str): 会議ID
        
    Returns:
        Optional[Dict]: 会議フィードバック
        Noneの場合は会議が見つからないか、データ形式が不正
    """
    # 会議の基本情報を取得
    meeting_ref = Config.get_db_client().collection(FIRESTORE_MEETING_COLLECTION).document(meeting_id)
    meeting_doc = meeting_ref.get()
    
    if not meeting_doc.exists:
        return None
    
    meeting_data = meeting_doc.to_dict()
    
    # 会話履歴を取得
    message_history = get_message_history(meeting_id)
    
    # 日時の変換（JST）
    date = meeting_data["start_date"]
    start_time = meeting_data["start_time"]
    end_time = meeting_data["end_time"]
    start_at = f"{date} {start_time}:00"
    end_at = f"{date} {end_time}:00"
    agenda = meeting_data.get("agenda")

    try:
        # MeetingInputを構築
        meeting_input = MeetingInput(
            purpose=meeting_data.get("meeting_purpose"),
            agenda=agenda,
            participants=meeting_data.get("participants", []),
            comment_history=message_history if isinstance(message_history, list) else [message_history],
            start_at=start_at,
            end_at=end_at
        )
    except Exception as e:
        print(f"Error creating MeetingInput: {e}")
        return None
    
    # フィードバックを生成
    feedback = process_meeting_feedback(meeting_input)
    
    # AIのフィードバックを発言履歴用DBに保存する
    post_message(meeting_id, Config.get_ai_facilitator_name(), feedback.message, meta={"role": "ai", "type": "feedback"})
    
    return feedback
