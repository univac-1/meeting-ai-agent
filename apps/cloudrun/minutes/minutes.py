from typing import List
from message.message import get_message_history
from config import Config
from minutes.constants import MinutesFields
from meeting.meeting import AgendaItem
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
            MinutesFields.AGENDA: [],
            MinutesFields.DECISIONS: [],
            MinutesFields.ACTION_PLAN: [],
        }
    )


def should_update_minutes(message_history: list, existing_minutes: dict) -> dict:
    vertexai.init(project=Config.PROJECT_ID, location="us-central1")

    determine_update_func = FunctionDeclaration(
        name="determine_update_requirements",
        description=(
            "Determine whether to add, update, or delete meeting minutes items based on the latest statement. "
            "Consider past discussions and existing records to ensure consistency."
        ),
        parameters={
            "type": "object",
            "properties": {
                "add_decision": {
                    "type": "boolean",
                    "description": "Whether a new decision should be added to the minutes.",
                },
                "add_decision_text": {
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
                "add_action_plan_text": {
                    "type": "string",
                    "description": "Text of the action plan to be added.",
                },
                "add_assigned_to": {
                    "type": "string",
                    "description": "Person responsible for the action plan (leave empty if unknown)",
                },
                "add_due_date": {
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

    latest_message = message_history[-1]  # 最新の発言
    past_messages = message_history[:-1]  # それ以前の履歴

    # 過去の会話履歴のフォーマット
    formatted_history = (
        "\n".join(
            [
                f"{msg.get('speak_at', '不明な時間')} - {msg.get('speaker', '不明な発言者')}: {msg.get('message', '発言なし')}"
                for msg in past_messages
            ]
        )
        or "なし"
    )

    # 最新の発言のフォーマット
    latest_message_text = (
        f"{latest_message.get('speak_at', '不明な時間')} - {latest_message.get('speaker', '不明な発言者')}: {latest_message.get('message', '発言なし')}"
        if latest_message
        else "なし"
    )

    # 既存の決定事項のフォーマット
    existing_decisions = (
        "\n".join(
            [
                f"- {d.get('text', '不明な決定')} (ID: {d.get('id', '不明')})"
                for d in existing_minutes.get(MinutesFields.DECISIONS, [])
            ]
        )
        or "なし"
    )

    # 既存のアクションプランのフォーマット
    existing_actions = (
        "\n".join(
            [
                f"- {a.get('task', '不明なアクション')} (ID: {a.get('id', '不明')}, 担当: {a.get('assigned_to', '未設定')}, 期限: {a.get('due_date', '未設定')})"
                for a in existing_minutes.get(MinutesFields.ACTION_PLAN, [])
            ]
        )
        or "なし"
    )

    full_message = f"""
    ## 最新の発言:
    {latest_message_text}

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
        add_decision_text = decision_action.get("add_decision_text")
        if add_decision_text:
            existing_decisions = existing_minutes.get(MinutesFields.DECISIONS, [])

            if any(d["text"] == add_decision_text for d in existing_decisions):
                print(f"⚠️ [スキップ] 同じ決定事項が既に存在: {add_decision_text}")
            else:
                new_decision = {
                    "id": f"decision_{uuid4().hex}",
                    "text": add_decision_text,
                }
                print(f"✅ [追加] 新しい決定事項: {new_decision}")
                doc_ref.update(
                    {MinutesFields.DECISIONS: firestore.ArrayUnion([new_decision])}
                )

    # --- 決定事項の更新 ---
    if decision_action.get("update_decision"):
        decisions = existing_minutes.get(MinutesFields.DECISIONS, [])
        target_id = decision_action["decision_id"]
        new_decision_text = decision_action.get("new_decision_text")
        if new_decision_text:
            print(f"🛠 [更新開始] 決定事項 ID: {target_id}")
            found = False
            for decision in decisions:
                if decision["id"] == target_id:
                    old_text = decision["text"]
                    decision["text"] = new_decision_text
                    print(
                        f"🔄 [更新完了] ID: {target_id} | 旧: '{old_text}' → 新: '{decision['text']}'"
                    )
                    found = True
                    break
            if not found:
                print(
                    f"❌ [エラー] 更新対象の決定事項 (ID: {target_id}) が見つかりません"
                )
            doc_ref.update({MinutesFields.DECISIONS: decisions})

    # --- 決定事項の削除 ---
    if decision_action.get("delete_decision"):
        decision_id_to_delete = decision_action["decision_id_to_delete"]
        decisions_before = existing_minutes.get(MinutesFields.DECISIONS, [])
        print(f"🗑 [削除試行] 決定事項 ID: {decision_id_to_delete}")
        decisions = [d for d in decisions_before if d["id"] != decision_id_to_delete]
        if len(decisions_before) == len(decisions):
            print(
                f"❌ [エラー] 削除対象の決定事項 (ID: {decision_id_to_delete}) が見つかりません"
            )
        else:
            print(f"✅ [削除完了] 決定事項 ID: {decision_id_to_delete}")
        doc_ref.update({MinutesFields.DECISIONS: decisions})

    # --- アクションプランの追加 ---
    if decision_action.get("add_action_plan"):
        new_action_text = decision_action.get("add_action_plan_text")
        if new_action_text:
            existing_actions = existing_minutes.get(MinutesFields.ACTION_PLAN, [])

            if any(a["task"] == new_action_text for a in existing_actions):
                print(f"⚠️ [スキップ] 同じアクションプランが既に存在: {new_action_text}")
            else:
                new_action = {
                    "id": f"action_{uuid4().hex}",
                    "task": new_action_text,
                    "assigned_to": decision_action.get("add_assigned_to", "未設定"),
                    "due_date": decision_action.get("add_due_date", "未設定"),
                }
                print(f"✅ [追加] 新しいアクションプラン: {new_action}")
                doc_ref.update(
                    {MinutesFields.ACTION_PLAN: firestore.ArrayUnion([new_action])}
                )

    # --- アクションプランの更新 ---
    if decision_action.get("update_action_plan"):
        actions = existing_minutes.get(MinutesFields.ACTION_PLAN, [])
        target_action_id = decision_action["action_id"]
        new_action_text = decision_action.get("new_action_text")
        if new_action_text:
            print(f"🛠 [更新開始] アクションプラン ID: {target_action_id}")
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
                        f"🔄 [更新完了] ID: {target_action_id} | 旧: {old_action} → 新: {action}"
                    )
                    found = True
                    break
            if not found:
                print(
                    f"❌ [エラー] 更新対象のアクションプラン (ID: {target_action_id}) が見つかりません"
                )
            doc_ref.update({MinutesFields.ACTION_PLAN: actions})

    # --- アクションプランの削除 ---
    if decision_action.get("delete_action_plan"):
        action_id_to_delete = decision_action["action_id_to_delete"]
        actions_before = existing_minutes.get(MinutesFields.ACTION_PLAN, [])
        print(f"🗑 [削除試行] アクションプラン ID: {action_id_to_delete}")
        actions = [a for a in actions_before if a["id"] != action_id_to_delete]
        if len(actions_before) == len(actions):
            print(
                f"❌ [エラー] 削除対象のアクションプラン (ID: {action_id_to_delete}) が見つかりません"
            )
        else:
            print(f"✅ [削除完了] アクションプラン ID: {action_id_to_delete}")
        doc_ref.update({MinutesFields.ACTION_PLAN: actions})


def set_agenda_in_minutes(meeting_id: str, agenda: List[AgendaItem]):
    """アジェンダを議事録DBに書き込む"""

    doc_ref = (
        db_client.collection(Config.FIRESTORE_MEETING_COLLECTION)
        .document(meeting_id)
        .collection(Config.FIRESTORE_MINUTES_COLLECTION)
        .document(Config.FIRESTORE_ALL_MINUTES_DOCUMENT)
    )

    doc_ref.set(
        {
            MinutesFields.AGENDA: [
                {"id": ind + 1, "completed": False, **ele}
                for ind, ele in enumerate(agenda)
            ],
            MinutesFields.DECISIONS: [],
            MinutesFields.ACTION_PLAN: [],
        }
    )
