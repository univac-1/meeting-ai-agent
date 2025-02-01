from typing import Dict, List, Optional, TypedDict
from typing_extensions import TypedDict
from datetime import datetime
from enum import Enum

class Message(TypedDict):
    """会議中の発言を表す型"""
    speaker: str
    content: str
    meta: Optional[Dict[str, str]]

# アジェンダ項目の型定義
class AgendaItem(TypedDict):
    """アジェンダ項目の型定義"""
    topic: str
    duration: int

# 会議の型定義
class Meeting(TypedDict):
    """会議の型定義"""
    meeting_name: str
    meeting_purpose: str
    start_date: str
    start_time: str
    end_time: str
    participants: List[str]
    agenda: List[AgendaItem]

class InterventionStatus(str, Enum):
    """介入リクエストの状態を表す列挙型"""
    PENDING = "pending"
    COMPLETED = "completed"

class InterventionRequest(TypedDict):
    """介入リクエストを表す型"""
    status: InterventionStatus
    reason: str
    created_at: datetime
    updated_at: datetime

class MeetingInput(TypedDict):
    """会議の入力情報を表す型"""
    purpose: str
    agenda: List[str]
    participants: List[str]
    comment_history: List[Message]
    start_at: str
    end_at: str
    intervention_request: Optional[InterventionRequest]

