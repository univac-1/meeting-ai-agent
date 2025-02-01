import json
import os
from models import MeetingInput, Message
from agent.intervention_check_agent import should_intervene

def load_test_data(filename: str) -> dict:
    """テストデータを読み込む"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "data", filename)
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def convert_to_meeting_input(data: dict) -> MeetingInput:
    """テストデータをMeetingInput形式に変換"""
    # コメント履歴をMessage型に変換
    comment_history = [
        {
            "speaker": comment["speaker"],
            "content": comment["message"],
            "meta": {"speak_at": comment["speak_at"]}
        }
        for comment in data["comment_history"]
    ]
    
    # アジェンダを文字列のリストに変換
    agenda = [item["topic"] for item in data["agenda"]]
    
    # 日時を変換
    start_at = f"{data['start_date']} {data['start_time']}:00"
    end_at = f"{data['start_date']} {data['end_time']}:00"
    
    return {
        "purpose": data["meeting_purpose"],
        "agenda": agenda,
        "participants": data["participants"],
        "comment_history": comment_history,
        "start_at": start_at,
        "end_at": end_at,
        "intervention_request": None
    }

def test_should_intervene_true():
    """介入が必要なケースのテスト"""
    # テストデータの読み込み
    data = load_test_data("test_intervention_check_agent_true_input.json")
    meeting_input = convert_to_meeting_input(data)
    
    # 介入判定の実行
    is_needed, reason = should_intervene(meeting_input)
    
    # デバッグ出力
    print(f"\nIntervention check result (true case):")
    print(f"is_needed: {is_needed}")
    print(f"reason: {reason}")
    
    # アサーション
    assert is_needed is True
    assert reason is not None
    assert len(reason) > 0

def test_should_intervene_false():
    """介入が不要なケースのテスト"""
    # テストデータの読み込み
    data = load_test_data("test_intervention_check_agent_false_input.json")
    meeting_input = convert_to_meeting_input(data)
    
    # 介入判定の実行
    is_needed, reason = should_intervene(meeting_input)
    
    # デバッグ出力
    print(f"\nIntervention check result (false case):")
    print(f"is_needed: {is_needed}")
    print(f"reason: {reason}")
    
    # アサーション
    assert is_needed is False
    assert isinstance(reason, str)
    assert len(reason) > 0 