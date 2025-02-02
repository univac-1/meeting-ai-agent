from typing import Dict, Optional
from config import Config
from message.message import get_message_history, post_message
from agent.feedback_agent import process_meeting_feedback, MeetingInput, AgendaItem as FeedbackAgendaItem
from agent.feedback_repository import post_feedback

FIRESTORE_MEETING_COLLECTION = Config.FIRESTORE_MEETING_COLLECTION


def generate_feedback(meeting_id: str) -> Optional[Dict]:
    """
    指定された会議IDに対するエージェントのフィードバックを生成します。
    
    Args:
        meeting_id (str): 会議ID
        
    Returns:
        Optional[Dict]: 会議フィードバック（アジェンダ、要約、評価、改善提案）
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
    
    # アジェンダの変換（存在する場合）
    agenda = [
            FeedbackAgendaItem(topic=item["topic"], duration=item["duration"])
            for item in meeting_data["agenda"]
    ]

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
    # 補足情報をDBに保存 
    post_feedback(meeting_id, feedback.message, feedback.detail.model_dump())
    
    return {
        "message": feedback.message,
        "detail": {
            "summary": feedback.detail.summary,
            "evaluation": feedback.detail.evaluation.model_dump()
        }
    }
