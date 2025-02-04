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
from uuid import uuid4

db_client = Config.get_db_client()


def get_existing_minutes(meeting_id: str) -> dict:
    doc_ref = (
        db_client.collection(Config.FIRESTORE_MEETING_COLLECTION)
        .document(meeting_id)
        .collection(Config.FIRESTORE_MINUTES_COLLECTION)
        .document(Config.FIRESTORE_ALL_MINUTES_DOCUMENT)
    )
    doc = doc_ref.get()
    return (
        doc.to_dict()
        if doc.exists
        else {
            MinutesFields.DECISIONS: [],
            MinutesFields.ACTION_PLAN: [],
        }
    )


def should_update_minutes(message_history: list, existing_minutes: dict) -> dict:
    vertexai.init(project=Config.PROJECT_ID, location="us-central1")

    determine_update_func = FunctionDeclaration(
        name="determine_update_requirements",
        description="Determine whether to add, update, or delete meeting minutes items based on past discussions and existing records.",
        parameters={
            "type": "object",
            "properties": {
                "add_decision": {
                    "type": "boolean",
                    "description": "Whether a new decision should be added to the minutes.",
                },
                "decision_text": {
                    "type": "string",
                    "description": "Text content of the decision to be added.",
                },
                "update_decision": {
                    "type": "boolean",
                    "description": "Whether an existing decision should be updated.",
                },
                "decision_id": {
                    "type": "string",
                    "description": "ID of the decision to update.",
                },
                "new_decision_text": {
                    "type": "string",
                    "description": "New text for the decision being updated.",
                },
                "delete_decision": {
                    "type": "boolean",
                    "description": "Whether an existing decision should be deleted.",
                },
                "decision_id_to_delete": {
                    "type": "string",
                    "description": "ID of the decision to be deleted.",
                },
                "add_action_plan": {
                    "type": "boolean",
                    "description": "Whether a new action plan should be added.",
                },
                "action_plan_text": {
                    "type": "string",
                    "description": "Text of the action plan to be added.",
                },
                "assigned_to": {
                    "type": "string",
                    "description": "Person responsible for the action plan (leave empty if unknown)",
                },
                "due_date": {
                    "type": "string",
                    "description": "If the due date is uncertain, leave it empty. Do NOT guess an approximate date. Use YYYY-MM-DD format only for confirmed deadlines.",
                },
                "update_action_plan": {
                    "type": "boolean",
                    "description": "Whether an existing action plan should be updated.",
                },
                "action_id": {
                    "type": "string",
                    "description": "ID of the action plan to update.",
                },
                "new_action_text": {
                    "type": "string",
                    "description": "New text for the action plan being updated.",
                },
                "new_assigned_to": {
                    "type": "string",
                    "description": "New person assigned to the action plan (leave empty if unknown)",
                },
                "new_due_date": {
                    "type": "string",
                    "description": "If the new due date is uncertain, leave it empty. Do NOT guess an approximate date. Use YYYY-MM-DD format only for confirmed deadlines.",
                },
                "delete_action_plan": {
                    "type": "boolean",
                    "description": "Whether an existing action plan should be deleted.",
                },
                "action_id_to_delete": {
                    "type": "string",
                    "description": "ID of the action plan to be deleted.",
                },
            },
        },
    )

    tool = Tool(function_declarations=[determine_update_func])
    model = GenerativeModel(
        "gemini-1.5-flash-002",
        tools=[tool],
        tool_config=ToolConfig(
            function_calling_config=ToolConfig.FunctionCallingConfig(
                mode=ToolConfig.FunctionCallingConfig.Mode.ANY
            )
        ),
    )

    formatted_history = "\n".join(
        [
            f"{msg['speak_at']} - {msg['speaker']}: {msg['message']}"
            for msg in message_history
        ]
    )
    existing_decisions = "\n".join(
        [
            f"- {d['text']} (ID: {d['id']})"
            for d in existing_minutes.get(MinutesFields.DECISIONS, [])
        ]
    )
    existing_actions = "\n".join(
        [
            f"- {a['task']} (ID: {a['id']}, 担当: {a['assigned_to']}, 期限: {a['due_date']})"
            for a in existing_minutes.get(MinutesFields.ACTION_PLAN, [])
        ]
    )

    full_message = f"""
    ## 過去の会話履歴:
    {formatted_history}

    ## 既存の決定事項:
    {existing_decisions}

    ## 既存のアクションプラン:
    {existing_actions}
    """

    response = model.generate_content(full_message)
    function_calls = (
        response.candidates[0].function_calls if response.candidates else []
    )
    return function_calls[0].args if function_calls else {}


def update_minutes(meeting_id: str):
    message_history = get_message_history(meeting_id, 10)
    existing_minutes = get_existing_minutes(meeting_id)
    decision_action = should_update_minutes(message_history, existing_minutes)

    doc_ref = (
        db_client.collection(Config.FIRESTORE_MEETING_COLLECTION)
        .document(meeting_id)
        .collection(Config.FIRESTORE_MINUTES_COLLECTION)
        .document(Config.FIRESTORE_ALL_MINUTES_DOCUMENT)
    )

    if not doc_ref.get().exists:
        doc_ref.set(
            {
                MinutesFields.AGENDA: [],
                MinutesFields.DECISIONS: [],
                MinutesFields.ACTION_PLAN: [],
            }
        )

    # --- 決定事項の追加 ---
    if decision_action.get("add_decision"):
        new_decision = {
            "id": f"decision_{uuid4().hex}",
            "text": decision_action["decision_text"],
        }
        print("新しい決定事項を追加します:", new_decision)
        doc_ref.update({MinutesFields.DECISIONS: firestore.ArrayUnion([new_decision])})

    # --- 決定事項の更新 ---
    if decision_action.get("update_decision"):
        decisions = existing_minutes.get(MinutesFields.DECISIONS, [])
        target_id = decision_action["decision_id"]
        print("決定事項の更新を開始します。対象ID:", target_id)
        found = False
        for decision in decisions:
            if decision["id"] == target_id:
                old_text = decision["text"]
                decision["text"] = decision_action["new_decision_text"]
                print(
                    f"決定事項(ID: {target_id})のテキストを更新しました。旧テキスト: '{old_text}' → 新テキスト: '{decision['text']}'"
                )
                found = True
                break
        if not found:
            print(f"更新対象の決定事項(ID: {target_id})が見つかりませんでした。")
        doc_ref.update({MinutesFields.DECISIONS: decisions})

    # --- 決定事項の削除 ---
    if decision_action.get("delete_decision"):
        decision_id_to_delete = decision_action["decision_id_to_delete"]
        decisions_before = existing_minutes.get(MinutesFields.DECISIONS, [])
        print("決定事項の削除を試みます。対象ID:", decision_id_to_delete)
        decisions = [d for d in decisions_before if d["id"] != decision_id_to_delete]
        if len(decisions_before) == len(decisions):
            print(
                f"削除対象の決定事項(ID: {decision_id_to_delete})が見つかりませんでした。"
            )
        else:
            print(f"決定事項(ID: {decision_id_to_delete})を削除しました。")
        doc_ref.update({MinutesFields.DECISIONS: decisions})

    # --- アクションプランの追加 ---
    if decision_action.get("add_action_plan"):
        new_action = {
            "id": f"action_{uuid4().hex}",
            "task": decision_action["action_plan_text"],
            "assigned_to": decision_action["assigned_to"],
            "due_date": decision_action["due_date"],
        }
        print("新しいアクションプランを追加します:", new_action)
        doc_ref.update({MinutesFields.ACTION_PLAN: firestore.ArrayUnion([new_action])})

    # --- アクションプランの更新 ---
    if decision_action.get("update_action_plan"):
        actions = existing_minutes.get(MinutesFields.ACTION_PLAN, [])
        target_action_id = decision_action["action_id"]
        print("アクションプランの更新を開始します。対象ID:", target_action_id)
        found = False
        for action in actions:
            if action["id"] == target_action_id:
                old_action = action.copy()  # 旧値を記録
                action.update(
                    {
                        "task": decision_action["new_action_text"],
                        "assigned_to": decision_action.get(
                            "new_assigned_to", action["assigned_to"]
                        ),
                        "due_date": decision_action.get(
                            "new_due_date", action["due_date"]
                        ),
                    }
                )
                print(
                    f"アクションプラン(ID: {target_action_id})を更新しました。旧値: {old_action} → 新値: {action}"
                )
                found = True
                break
        if not found:
            print(
                f"更新対象のアクションプラン(ID: {target_action_id})が見つかりませんでした。"
            )
        doc_ref.update({MinutesFields.ACTION_PLAN: actions})

    # --- アクションプランの削除 ---
    if decision_action.get("delete_action_plan"):
        action_id_to_delete = decision_action["action_id_to_delete"]
        actions_before = existing_minutes.get(MinutesFields.ACTION_PLAN, [])
        print("アクションプランの削除を試みます。対象ID:", action_id_to_delete)
        actions = [a for a in actions_before if a["id"] != action_id_to_delete]
        if len(actions_before) == len(actions):
            print(
                f"削除対象のアクションプラン(ID: {action_id_to_delete})が見つかりませんでした。"
            )
        else:
            print(f"アクションプラン(ID: {action_id_to_delete})を削除しました。")
        doc_ref.update({MinutesFields.ACTION_PLAN: actions})
