from flask import Flask, request, jsonify
from typing import Dict

from agent.meeting_feedback_graph import process_meeting_feedback, MeetingInput
from flask_cors import CORS

from message.message import post_message, get_message_history
from meeting.meeting import create_meeting
from config import Config

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
    meeting_name = data.get("meeting_name")
    participants = data.get("participants")
    agenda = data.get("agenda")

    meeting_id = create_meeting(meeting_name, participants, agenda)

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
    # 会議の基本情報を取得
    meeting_ref = Config.get_db_client().collection("meetings").document(meeting_id)
    meeting_doc = meeting_ref.get()
    
    if not meeting_doc.exists:
        return jsonify({"error": "Meeting not found"}), 404
        
    meeting_data = meeting_doc.to_dict()
    print("Meeting data:", meeting_data)  # デバッグ用ログ
    
    # 会話履歴を取得
    message_history = get_message_history(meeting_id)
    print("Message history:", message_history)  # デバッグ用ログ
    
    # MeetingInputを構築
    try:
        meeting_input = MeetingInput(
            purpose=meeting_data.get("purpose", "会議の目的"),
            agenda=meeting_data.get("agenda", []),
            participants=meeting_data.get("participants", []),
            comment_history=message_history if isinstance(message_history, list) else [message_history]
        )
    except Exception as e:
        print("Error creating MeetingInput:", e)
        print("message_history type:", type(message_history))
        print("message_history content:", message_history)
        return jsonify({"error": "Invalid meeting data format"}), 500
    
    feedback = process_meeting_feedback(meeting_input)

    # AIのフィードバックをDB保存する
    post_message(meeting_id, feedback["speaker"], feedback["message"], feedback.get("detail"))

    return jsonify({"data": feedback}), 200

@app.route('/message', methods=["POST"])
def message():
    data = request.get_json()
    meeting_id = data.get("meeting_id")
    speaker = data.get("speaker")
    message = data.get("message")

    post_message(meeting_id, speaker, message)

    return jsonify({"data": "OK"}), 201


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
