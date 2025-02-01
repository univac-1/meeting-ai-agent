from flask import Flask, request, jsonify
from typing import Dict

from cloudrun.agent.feedback_agent import process_meeting_feedback, MeetingInput, AgendaItem as FeedbackAgendaItem
from flask_cors import CORS

from message.message import post_message, get_message_history
from meeting.meeting import create_meeting, update_meeting, MeetingUpdateFields, AgendaItem as MeetingAgendaItem
from config import Config
from agent.intervention_service import handle_message_intervention, generate_intervention_message
from agent.intervention_request_service import request_intervention
from cloudrun.agent.feedback_service import generate_feedback
import json
FIRESTORE_MEETING_COLLECTION = Config.FIRESTORE_MEETING_COLLECTION

app = Flask(__name__)
app.json.ensure_ascii = False

# CORSを有効化
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def hello_world():
    return 'Hello Cloud Run!'

@app.route('/meeting', methods=["POST"])
def meeting():
    data = request.get_json()  # リクエストからデータを取得
    meeting_name = data["meeting_name"]
    meeting_purpose = data["meeting_purpose"]
    start_date = data["start_date"]
    start_time = data["start_time"]
    end_time = data["end_time"]
    participants = data["participants"]
    # アジェンダの変換
    meeting_agenda = [
        MeetingAgendaItem(topic=item["topic"], duration=int(item["duration"]))
        for item in data["agenda"]
    ]

    # 会議の作成処理
    meeting_id = create_meeting(
        meeting_name, participants, meeting_agenda, start_date, start_time, end_time, meeting_purpose
    )

    return jsonify({"data": {"meeting_id": meeting_id}}), 201

@app.route("/meeting/<meeting_id>/agent-feedback", methods=["GET"])
def get_meeting_feedback(meeting_id: str) -> Dict:
    """
    指定された会議IDに対するエージェントのフィードバックを取得します。
    
    Args:
        meeting_id (str): 会議ID
        
    Returns:
        Dict: 会議フィードバック（アジェンダ、要約、評価、改善提案）
    """
    feedback = generate_feedback(meeting_id)
    if feedback is None:
        return jsonify({"error": "Meeting not found or invalid data format"}), 404
    
    return jsonify({"data": feedback}), 200

@app.route('/message', methods=["POST"])
def message():
    data = request.get_json()
    meeting_id = data.get("meeting_id")
    speaker = data.get("speaker")
    message = data.get("message")

    # メッセージを保存
    post_message(meeting_id, speaker, message)
    
    # TODO これ自体を別のendpointに分離したい気分ではある
    request_intervention(meeting_id)
    
    return jsonify({"data": "OK"}), 201

@app.route('/intervention/<meeting_id>', methods=["GET"])
def allow_intervention(meeting_id: str):
    """介入許可を受け取り、介入メッセージを生成する"""
    # 介入メッセージを生成して保存
    intervention_message = generate_intervention_message(meeting_id)
    return jsonify({"data": {"message": intervention_message}}), 200
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
