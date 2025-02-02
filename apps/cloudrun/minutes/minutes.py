from message.message import get_message_history
from config import Config
from minutes.constants import MinutesFields, ActionPlanFields
import vertexai
from vertexai.preview.generative_models import (
    FunctionDeclaration,
    GenerativeModel,
    Tool,
    ToolConfig,
)

from google.cloud import firestore

db_client = Config.get_db_client()


def get_existing_minutes(meeting_id: str) -> dict:
    """
    Firestore から既存の議事録を取得する。
    取得できない場合は空の辞書を返す。
    """
    doc_ref = (
        db_client.collection(Config.FIRESTORE_MEETING_COLLECTION)
        .document(meeting_id)
        .collection(Config.FIRESTORE_MINUTES_COLLECTION)
        .document(Config.FIRESTORE_ALL_MINUTES_DOCUMENT)
    )

    doc = doc_ref.get()
    if not doc.exists:
        return {
            MinutesFields.DECISIONS: [],
            MinutesFields.ACTION_PLAN: [],
        }

    return doc.to_dict()


def should_update_minutes(message_history: list, existing_minutes: dict) -> dict:
    """
    Function Calling を利用して、過去の会話履歴と既存の議事録を考慮し、
    決定事項およびアクションプランの追加が必要かを判定し、適切な文言・担当者・期限を決定する。
    """
    vertexai.init(project=Config.PROJECT_ID, location="us-central1")

    determine_update_func = FunctionDeclaration(
        name="determine_update_requirements",
        description="Determine whether to update meeting minutes with decisions and action plans, considering past discussions and existing records.",
        parameters={
            "type": "object",
            "properties": {
                "add_decision": {
                    "type": "boolean",
                    "description": "Whether a decision should be added",
                },
                "decision_text": {
                    "type": "string",
                    "description": "Text to add as a decision in the meeting minutes",
                },
                "add_action_plan": {
                    "type": "boolean",
                    "description": "Whether an action plan should be added. Only set to true if there is a clear, actionable next step that requires tracking and follow-up.",
                },
                "action_plan_text": {
                    "type": "string",
                    "description": "Text to add as an action plan in the meeting minutes",
                },
                "assigned_to": {
                    "type": "string",
                    "description": "Person responsible for the action plan (leave empty if unknown)",
                },
                "due_date": {
                    "type": "string",
                    "description": "If the due date is uncertain, leave it empty. Do NOT guess an approximate date. Use YYYY-MM-DD format only for confirmed deadlines.",
                },
            },
        },
    )

    tool = Tool(function_declarations=[determine_update_func])

    model = GenerativeModel(
        model_name="gemini-1.5-flash-002",
        tools=[tool],
        tool_config=ToolConfig(
            function_calling_config=ToolConfig.FunctionCallingConfig(
                mode=ToolConfig.FunctionCallingConfig.Mode.ANY,
                allowed_function_names=["determine_update_requirements"],
            )
        ),
    )

    # メッセージ履歴を整形
    formatted_history = "\n".join(
        [
            f"{msg['speak_at']} - {msg['speaker']}: {msg['message']}"
            for msg in message_history
        ]
    )

    # 既存の決定事項とアクションプランを取得
    existing_decisions = "\n".join(existing_minutes.get(MinutesFields.DECISIONS, []))
    existing_actions = "\n".join(
        [
            f"- {action[ActionPlanFields.TASK]} (担当: {action[ActionPlanFields.ASSIGNED_TO]}, 期限: {action[ActionPlanFields.DUE_DATE]})"
            for action in existing_minutes.get(MinutesFields.ACTION_PLAN, [])
        ]
    )

    # LLM に送るメッセージ
    full_message = f"""
    ## 過去の会話履歴:
    {formatted_history}

    ## 既存の決定事項:
    {existing_decisions}

    ## 既存のアクションプラン:
    {existing_actions}
    """

    response = model.generate_content(full_message)

    function_calls = response.candidates[0].function_calls

    if function_calls:
        first_call = function_calls[0]
        if hasattr(first_call, "args"):
            return first_call.args

    return {
        "add_decision": False,
        "decision_text": "",
        "add_action_plan": False,
        "action_plan_text": "",
        "assigned_to": "",
        "due_date": "",
    }


def update_minutes(meeting_id: str, message: str):
    """
    議事録の更新が必要か判定し、必要であれば更新する。
    """
    message_history = get_message_history(meeting_id, 10)
    print(f"最新の発言：{message_history[-1]}")
    existing_minutes = get_existing_minutes(meeting_id)

    decision_action = should_update_minutes(message_history, existing_minutes)

    add_decision = decision_action.get("add_decision", False)
    decision_text = decision_action.get("decision_text", "").strip()

    add_action_plan = decision_action.get("add_action_plan", False)
    action_plan_text = decision_action.get("action_plan_text", "").strip()
    assigned_to = decision_action.get("assigned_to", "").strip() or "未割当"
    due_date = decision_action.get("due_date", "").strip() or "未設定"

    if not add_decision and not add_action_plan:
        print(f"📝 議事録更新不要:{meeting_id} - {message}")
        return

    doc_ref = (
        db_client.collection(Config.FIRESTORE_MEETING_COLLECTION)
        .document(meeting_id)
        .collection(Config.FIRESTORE_MINUTES_COLLECTION)
        .document(Config.FIRESTORE_ALL_MINUTES_DOCUMENT)
    )

    if not doc_ref.get().exists:
        print(f"⚠️ ドキュメントが存在しません: {meeting_id}. 新しく作成します。")
        doc_ref.set(
            {
                MinutesFields.AGENDA: [],
                MinutesFields.DECISIONS: [],
                MinutesFields.ACTION_PLAN: [],
            }
        )  # 初期値をセット

    if add_decision and decision_text:
        doc_ref.update({MinutesFields.DECISIONS: firestore.ArrayUnion([decision_text])})
        print(f"✅ 決定事項を追加: {decision_text}")

    if add_action_plan and action_plan_text:
        new_action = {
            ActionPlanFields.TASK: action_plan_text,
            ActionPlanFields.ASSIGNED_TO: assigned_to,
            ActionPlanFields.DUE_DATE: due_date,
        }
        doc_ref.update({MinutesFields.ACTION_PLAN: firestore.ArrayUnion([new_action])})
        print(
            f"📌 アクションプランを追加: {action_plan_text}（担当: {assigned_to}, 期限: {due_date}）"
        )
