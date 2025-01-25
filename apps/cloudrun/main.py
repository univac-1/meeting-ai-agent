from flask import Flask, request, jsonify
from typing import Dict

from agent.conversation import handle_conversation
from agent.meeting_feedback_graph import process_meeting_feedback, MeetingInput
from flask_cors import CORS

from meeting.meeting import create_meeting

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

    return jsonify({"data": {"meeting_id": meeting_id}}), 200



@app.route("/meeting/<meeting_id>/agent-feedback", methods=["GET"])
def get_meeting_feedback(meeting_id: str) -> Dict:
    """
    指定された会議IDに対するエージェントのフィードバックを取得します。
    
    Args:
        meeting_id (str): 会議ID
        
    Returns:
        Dict: 会議フィードバック（アジェンダ、要約、評価、改善提案）
    """

        # テスト用のモックデータ
    mock_meetings: Dict[str, MeetingInput] = {
        "test-meeting": MeetingInput(
            purpose="プロダクトのアイデアを決める",
            agenda=["参加者からアイデアを募る", "参加者同士でアイデアを評価", "最も評価のよいものに決定"],
            participants=["ごん", "ぴとー", "ごれいぬ"],
            comment_history=[
                {"speaker": "ごん", "message": "ぼくは事務手続きの処理フローを可視化するツールを作りたい"},
                {"speaker": "ぴとー", "message": "それってネットで検索すればよくない?chatbotもある気がするけど"},
                {"speaker": "ごん", "message": "パスポートをとったときの話だけど、必要なフローを網羅するのに横断的にサイト検索しないといけないのは大変だったよ。"},
                {"speaker": "ぴとー", "message": "ごめん、なにいってるかよくわかんない。次"}
            ]
        )
    }

    if meeting_id not in mock_meetings:
        return jsonify({"error": "Meeting not found"}), 404
    
    meeting_input = mock_meetings[meeting_id]
    feedback = process_meeting_feedback(meeting_input)
    return jsonify(feedback)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
