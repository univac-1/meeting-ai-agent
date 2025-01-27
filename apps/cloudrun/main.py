from flask import Flask, request, jsonify
from typing import Dict

from agent.meeting_feedback_graph import process_meeting_feedback, MeetingInput
from flask_cors import CORS

from constants import FIRESTORE_MEETING_COLLECTION
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
    meeting_name = data["meeting_name"]
    meeting_purpose = data["meeting_purpose"]
    start_date = data["start_date"]
    start_time = data["start_time"]
    end_time = data["end_time"]
    participants = data["participants"]
    agenda = data["agenda"]

    # 会議の作成処理
    meeting_id = create_meeting(
        meeting_name, participants, agenda, start_date, start_time, end_time, meeting_purpose
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
    # 会議の基本情報を取得
    meeting_ref = Config.get_db_client().collection(FIRESTORE_MEETING_COLLECTION).document(meeting_id)
    meeting_doc = meeting_ref.get()
    
    if not meeting_doc.exists:
        return jsonify({"error": "Meeting not found"}), 404
        
    meeting_data = meeting_doc.to_dict()
    print("Meeting data:", meeting_data)  # デバッグ用ログ
    
    # 会話履歴を取得
    message_history = get_message_history(meeting_id)
    print("Message history:", message_history)  # デバッグ用ログ
    
    # 既存実装に合わせるためにアジェンダの "topic" だけを抽出した配列を生成
    agenda_topics = [item.get("topic", "") for item in meeting_data["agenda"]]

    # MeetingInputを構築
    try:
        meeting_input = MeetingInput(
            purpose=meeting_data.get("meeting_purpose"),
            agenda=agenda_topics,
            participants=meeting_data.get("participants", []),
            comment_history=message_history if isinstance(message_history, list) else [message_history]
        )
    except Exception as e:
        print("Error creating MeetingInput:", e)
        print("message_history type:", type(message_history))
        print("message_history content:", message_history)
        return jsonify({"error": "Invalid meeting data format"}), 500
    
    feedback = process_meeting_feedback(meeting_input)

    # AIのフィードバックを発言履歴用DBに保存する
    post_message(meeting_id, Config.get_ai_facilitator_name(), feedback["message"], meta={"voice": True, "role": "ai"})
    detail = feedback.get("detail", {})
    # detailsの処理
    for key, value in detail.items():
        if key == "agenda":
            message = "アジェンダは以下です。\n"    
            message += "\n".join(value)
            post_message(meeting_id, Config.get_ai_facilitator_name(), message, meta={"role": "ai"})
        elif key == "summary":
            message = "要約です。\n"
            message += value
            post_message(meeting_id, Config.get_ai_facilitator_name(), message, meta={"role": "ai"})
        elif key == "evaluation":
            message = "評価です。\n"
            message += value
            post_message(meeting_id, Config.get_ai_facilitator_name(), message, meta={"role": "ai"})
        elif key == "improvement":
            message = "改善提案です。\n"
            message += value
            post_message(meeting_id, Config.get_ai_facilitator_name(), message, meta={"role": "ai"}) 

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
