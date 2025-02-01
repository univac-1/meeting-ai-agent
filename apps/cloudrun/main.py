from flask import Flask, request, jsonify
from typing import Dict

from agent.meeting_feedback_graph import (
    process_meeting_feedback,
    MeetingInput,
    AgendaItem as FeedbackAgendaItem,
)
from flask_cors import CORS

from message.message import post_message, get_message_history
from meeting.meeting import (
    create_meeting,
    update_meeting,
    MeetingUpdateFields,
    AgendaItem as MeetingAgendaItem,
)
from config import Config
import json

FIRESTORE_MEETING_COLLECTION = Config.FIRESTORE_MEETING_COLLECTION

app = Flask(__name__)
app.json.ensure_ascii = False

# CORSを有効化
CORS(app, resources={r"/*": {"origins": "*"}})


@app.route("/")
def hello_world():
    return "Hello Cloud Run!"


@app.route("/meeting", methods=["POST"])
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
        meeting_name,
        participants,
        meeting_agenda,
        start_date,
        start_time,
        end_time,
        meeting_purpose,
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
    meeting_ref = (
        Config.get_db_client()
        .collection(FIRESTORE_MEETING_COLLECTION)
        .document(meeting_id)
    )
    meeting_doc = meeting_ref.get()

    if not meeting_doc.exists:
        return jsonify({"error": "Meeting not found"}), 404

    meeting_data = meeting_doc.to_dict()
    print("Meeting data:", meeting_data)  # デバッグ用ログ

    # 会話履歴を取得
    message_history = get_message_history(meeting_id)
    print("Message history:", message_history)  # デバッグ用ログ

    # 日時の変換（JST）
    date = meeting_data["start_date"]
    start_time = meeting_data["start_time"]
    end_time = meeting_data["end_time"]
    start_at = f"{date} {start_time}:00"
    end_at = f"{date} {end_time}:00"

    # アジェンダの変換（存在する場合）
    agenda = None
    if meeting_data.get("agenda"):
        agenda = [
            FeedbackAgendaItem(topic=item["topic"], duration=item["duration"])
            for item in meeting_data["agenda"]
        ]

    # MeetingInputを構築
    try:
        meeting_input = MeetingInput(
            purpose=meeting_data.get("meeting_purpose"),
            agenda=agenda,  # 既存のアジェンダがあればそれを使用、なければNone
            participants=meeting_data.get("participants", []),
            comment_history=(
                message_history
                if isinstance(message_history, list)
                else [message_history]
            ),
            start_at=start_at,
            end_at=end_at,
        )
    except Exception as e:
        print("Error creating MeetingInput:", e)
        print("message_history type:", type(message_history))
        print("message_history content:", message_history)
        return jsonify({"error": "Invalid meeting data format"}), 500

    feedback = process_meeting_feedback(meeting_input)

    # AIのフィードバックを発言履歴用DBに保存する
    post_message(
        meeting_id,
        Config.get_ai_facilitator_name(),
        feedback.message,
        meta={"role": "ai", "type": "feedback"},
    )
    detail = feedback.detail

    # 新しいアジェンダが生成された場合、会議情報を更新
    if detail.agenda is not None:
        # アジェンダメッセージの投稿
        message = "アジェンダです。\n"
        message += json.dumps(
            [
                {"topic": item.topic, "duration": item.duration}
                for item in detail.agenda
            ],
            ensure_ascii=False,
        )
        post_message(
            meeting_id,
            Config.get_ai_facilitator_name(),
            message,
            meta={"role": "ai", "type": "agenda"},
        )

        # 会議情報の更新
        update_data: MeetingUpdateFields = {
            "agenda": [
                {"topic": item.topic, "duration": item.duration}
                for item in detail.agenda
            ]
        }
        if not update_meeting(meeting_id, update_data):
            print(f"Failed to update meeting agenda for meeting_id: {meeting_id}")

    if detail.summary is not None:
        message = "要約です。\n"
        message += detail.summary
        post_message(
            meeting_id,
            Config.get_ai_facilitator_name(),
            message,
            meta={"role": "ai", "type": "summary"},
        )

    if detail.evaluation is not None:
        message = "評価です。\n"
        message += json.dumps(
            {
                "engagement": detail.evaluation.engagement,
                "concreteness": detail.evaluation.concreteness,
                "direction": detail.evaluation.direction,
            },
            ensure_ascii=False,
        )
        post_message(
            meeting_id,
            Config.get_ai_facilitator_name(),
            message,
            meta={"role": "ai", "type": "evaluation"},
        )

    return (
        jsonify(
            {
                "data": {
                    "message": feedback.message,
                    "detail": {
                        "summary": detail.summary,
                        "evaluation": (
                            detail.evaluation.model_dump()
                            if detail.evaluation
                            else None
                        ),
                        "agenda": (
                            [
                                {"topic": item.topic, "duration": item.duration}
                                for item in detail.agenda
                            ]
                            if detail.agenda
                            else None
                        ),
                    },
                }
            }
        ),
        200,
    )


@app.route("/message", methods=["POST"])
def message():
    data = request.get_json()
    meeting_id = data.get("meeting_id")
    speaker = data.get("speaker")
    message = data.get("message")

    post_message(meeting_id, speaker, message)

    return jsonify({"data": "OK"}), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
