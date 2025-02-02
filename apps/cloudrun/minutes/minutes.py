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


def should_update_minutes(message: str) -> dict:
    """
    Function calling を利用して、議事録の決定事項およびアクションプランの追加が必要か判定
    """
    vertexai.init(project=Config.PROJECT_ID, location="us-central1")

    determine_update_func = FunctionDeclaration(
        name="determine_update_requirements",
        description="Determine whether to update meeting minutes with decisions and action plans",
        parameters={
            "type": "object",
            "properties": {
                "add_decision": {
                    "type": "boolean",
                    "description": "Whether a decision should be added",
                },
                "add_action_plan": {
                    "type": "boolean",
                    "description": "Whether an action plan should be added",
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

    response = model.generate_content(message)

    function_calls = response.candidates[0].function_calls

    if function_calls:
        first_call = function_calls[0]
        if hasattr(first_call, "args"):
            return first_call.args

    return {"add_decision": False, "add_action_plan": False}


def update_minutes(meeting_id: str, message: str):
    """
    議事録の更新が必要か判定し、必要であればする
    """

    decision_action = should_update_minutes(message)

    add_decision = decision_action.get("add_decision", False)
    add_action_plan = decision_action.get("add_action_plan", False)

    if not add_decision and not add_action_plan:
        print(f"📝 更新不要: {message}")
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

    if add_decision:
        doc_ref.update({MinutesFields.DECISIONS: firestore.ArrayUnion([message])})
        print(f"✅ 決定事項を追加: {message}")

    if add_action_plan:
        new_action = {
            ActionPlanFields.TASK: message,  # タスクの内容
            ActionPlanFields.ASSIGNED_TO: "未割当",  # 担当者（デフォルト）
            ActionPlanFields.DUE_DATE: "未設定",  # 期限（デフォルト）
        }
        doc_ref.update({MinutesFields.ACTION_PLAN: firestore.ArrayUnion([new_action])})
        print(f"📌 アクションプランを追加: {message}")
