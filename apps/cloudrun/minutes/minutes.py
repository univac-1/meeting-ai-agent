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

    # アジェンダの完了判定を行う関数
    determine_update_agenda_completion = FunctionDeclaration(
        name="determine_update_agenda_completion",
        description=(
            "Determine whether agenda items have been completed based on the latest statement. "
            "Consider past discussions and existing records to ensure accuracy."
        ),
        parameters={
            "type": "object",
            "properties": {
                "completed_agenda_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of agenda IDs that have been completed.",
                }
            },
        },
    )

    # 決定事項の更新を判定する関数
    determine_update_decision = FunctionDeclaration(
        name="determine_update_decision",
        description=(
            "Determine whether to add, update, or delete decisions based on the latest statement. "
            "Ensure that the decision is expressed in a single line while considering past discussions and records."
        ),
        parameters={
            "type": "object",
            "properties": {
                "add_decision": {
                    "type": "boolean",
                    "description": "Whether to add a new decision.",
                },
                "add_decision_text": {
                    "type": "string",
                    "description": "Content of the new decision.",
                },
                "update_decision": {
                    "type": "boolean",
                    "description": "Whether to update an existing decision.",
                },
                "decision_id": {
                    "type": "string",
                    "description": "ID of the decision to update.",
                },
                "new_decision_text": {
                    "type": "string",
                    "description": "New text for the updated decision.",
                },
                "delete_decision": {
                    "type": "boolean",
                    "description": "Whether to delete an existing decision.",
                },
                "decision_id_to_delete": {
                    "type": "string",
                    "description": "ID of the decision to delete.",
                },
            },
        },
    )

    # アクションプランの更新を判定する関数
    determine_update_action_plan = FunctionDeclaration(
        name="determine_update_action_plan",
        description=(
            "Determine whether to add, update, or delete action plans based on the latest statement. "
            "Ensure that the action plan is expressed in a single line while considering past discussions and records."
        ),
        parameters={
            "type": "object",
            "properties": {
                "add_action_plan": {
                    "type": "boolean",
                    "description": "Whether to add a new action plan.",
                },
                "add_action_plan_text": {
                    "type": "string",
                    "description": "Text of the new action plan.",
                },
                "add_assigned_to": {
                    "type": "string",
                    "description": "Person responsible for the action plan (leave empty if unknown).",
                },
                "add_due_date": {
                    "type": "string",
                    "description": "Use YYYY-MM-DD format for confirmed deadlines; leave empty if uncertain.",
                },
                "update_action_plan": {
                    "type": "boolean",
                    "description": "Whether to update an existing action plan.",
                },
                "action_id": {
                    "type": "string",
                    "description": "ID of the action plan to update.",
                },
                "new_action_text": {
                    "type": "string",
                    "description": "New text for the updated action plan.",
                },
                "new_assigned_to": {
                    "type": "string",
                    "description": "New person assigned (leave empty if unknown).",
                },
                "new_due_date": {
                    "type": "string",
                    "description": "Use YYYY-MM-DD format for confirmed deadlines; leave empty if uncertain.",
                },
                "delete_action_plan": {
                    "type": "boolean",
                    "description": "Whether to delete an existing action plan.",
                },
                "action_id_to_delete": {
                    "type": "string",
                    "description": "ID of the action plan to delete.",
                },
            },
        },
    )

    tool = Tool(
        function_declarations=[
            determine_update_decision,
            determine_update_action_plan,
            determine_update_agenda_completion,
        ]
    )
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

    formatted_history = (
        "\n".join(
            [
                f"{msg.get('speak_at', '不明な時間')} - {msg.get('speaker', '不明な発言者')}: {msg.get('message', '発言なし')}"
                for msg in past_messages
            ]
        )
        or "なし"
    )

    latest_message_text = (
        f"{latest_message.get('speak_at', '不明な時間')} - {latest_message.get('speaker', '不明な発言者')}: {latest_message.get('message', '発言なし')}"
        if latest_message
        else "なし"
    )

    existing_decisions = (
        "\n".join(
            [
                f"- {d.get('text', '不明な決定')} (ID: {d.get('id', '不明')})"
                for d in existing_minutes.get(MinutesFields.DECISIONS, [])
            ]
        )
        or "なし"
    )

    existing_actions = (
        "\n".join(
            [
                f"- {a.get('task', '不明なアクション')} (ID: {a.get('id', '不明')}, 担当: {a.get('assigned_to', '未設定')}, 期限: {a.get('due_date', '未設定')})"
                for a in existing_minutes.get(MinutesFields.ACTION_PLAN, [])
            ]
        )
        or "なし"
    )

    existing_agenda = (
        "\n".join(
            [
                f"- {a.get('title', '不明なアジェンダ')} (ID: {a.get('id', '不明')}, 完了: {a.get('completed', '不明')})"
                for a in existing_minutes.get(MinutesFields.AGENDA, [])
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

    # 決定事項の更新判定
    response_decision = model.generate_content(full_message)
    function_calls_decision = (
        response_decision.candidates[0].function_calls
        if response_decision.candidates
        else []
    )
    decisions_update = next(
        (
            fc.args
            for fc in function_calls_decision
            if fc.name == "determine_update_decision"
        ),
        {},
    )

    # アクションプランの更新判定
    response_action = model.generate_content(full_message)
    function_calls_action = (
        response_action.candidates[0].function_calls
        if response_action.candidates
        else []
    )
    actions_update = next(
        (
            fc.args
            for fc in function_calls_action
            if fc.name == "determine_update_action_plan"
        ),
        {},
    )

    full_message = f"""
    ## 最新の発言:
    {latest_message_text}

    ## 過去の会話履歴:
    {formatted_history}

    ## 既存のアジェンダ:
    {existing_agenda}
    """

    # アジェンダ完了判定
    response_agenda = model.generate_content(full_message)
    function_calls_agenda = (
        response_agenda.candidates[0].function_calls
        if response_agenda.candidates
        else []
    )
    agenda_update = next(
        (
            fc.args
            for fc in function_calls_agenda
            if fc.name == "determine_update_agenda_completion"
        ),
        {},
    )

    return {
        "decisions_update": decisions_update,
        "actions_update": actions_update,
        "agenda_update": agenda_update,
    }


def update_minutes(meeting_id: str):
    message_history = get_message_history(meeting_id, 10)
    existing_minutes = get_existing_minutes(meeting_id)
    # 決定事項とアクションプランの更新情報を取得
    updates = should_update_minutes(message_history, existing_minutes)

    action_decisions = updates.get("decisions_update", {})
    action_actions = updates.get("actions_update", {})
    action_agenda = updates.get("agenda_update", {})

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
    if action_decisions.get("add_decision"):
        add_decision_text = action_decisions.get("add_decision_text")
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

    ### 決定事項の処理 ###
    # --- 決定事項の追加 ---
    if action_decisions.get("add_decision"):
        add_decision_text = action_decisions.get("add_decision_text")
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
    if action_decisions.get("update_decision"):
        target_id = action_decisions["decision_id"]
        new_decision_text = action_decisions.get("new_decision_text")
        if new_decision_text:
            print(f"🛠 [更新開始] 決定事項 ID: {target_id}")
            decisions = existing_minutes.get(MinutesFields.DECISIONS, [])
            for decision in decisions:
                if decision["id"] == target_id:
                    old_text = decision["text"]
                    decision["text"] = new_decision_text
                    print(
                        f"🔄 [更新完了] ID: {target_id} | 旧: '{old_text}' → 新: '{decision['text']}'"
                    )
                    break
            else:
                print(
                    f"❌ [エラー] 更新対象の決定事項 (ID: {target_id}) が見つかりません"
                )
            doc_ref.update({MinutesFields.DECISIONS: decisions})

    # --- 決定事項の削除 ---
    if action_decisions.get("delete_decision"):
        decision_id_to_delete = action_decisions.get("decision_id_to_delete")
        decisions_before = existing_minutes.get(MinutesFields.DECISIONS, [])
        decisions = [d for d in decisions_before if d["id"] != decision_id_to_delete]
        if len(decisions_before) == len(decisions):
            print(
                f"❌ [エラー] 削除対象の決定事項 (ID: {decision_id_to_delete}) が見つかりません"
            )
        else:
            print(f"✅ [削除完了] 決定事項 ID: {decision_id_to_delete}")
        doc_ref.update({MinutesFields.DECISIONS: decisions})

    ### アクションプランの処理 ###
    # --- アクションプランの追加 ---
    if action_actions.get("add_action_plan"):
        new_action_text = action_actions.get("add_action_plan_text")
        if new_action_text:
            existing_actions = existing_minutes.get(MinutesFields.ACTION_PLAN, [])
            if any(a["task"] == new_action_text for a in existing_actions):
                print(f"⚠️ [スキップ] 同じアクションプランが既に存在: {new_action_text}")
            else:
                new_action = {
                    "id": f"action_{uuid4().hex}",
                    "task": new_action_text,
                    "assigned_to": action_actions.get("add_assigned_to", "未設定"),
                    "due_date": action_actions.get("add_due_date", "未設定"),
                }
                print(f"✅ [追加] 新しいアクションプラン: {new_action}")
                doc_ref.update(
                    {MinutesFields.ACTION_PLAN: firestore.ArrayUnion([new_action])}
                )

    # --- アクションプランの更新 ---
    if action_actions.get("update_action_plan"):
        target_action_id = action_actions["action_id"]
        new_action_text = action_actions.get("new_action_text")
        if new_action_text:
            print(f"🛠 [更新開始] アクションプラン ID: {target_action_id}")
            actions = existing_minutes.get(MinutesFields.ACTION_PLAN, [])
            for action in actions:
                if action["id"] == target_action_id:
                    old_action = action.copy()  # 旧値を記録
                    action.update(
                        {
                            "task": new_action_text,
                            "assigned_to": action_actions.get(
                                "new_assigned_to", action["assigned_to"]
                            ),
                            "due_date": action_actions.get(
                                "new_due_date", action["due_date"]
                            ),
                        }
                    )
                    print(
                        f"🔄 [更新完了] ID: {target_action_id} | 旧: {old_action} → 新: {action}"
                    )
                    break
            else:
                print(
                    f"❌ [エラー] 更新対象のアクションプラン (ID: {target_action_id}) が見つかりません"
                )
            doc_ref.update({MinutesFields.ACTION_PLAN: actions})

    # --- アクションプランの削除 ---
    if action_actions.get("delete_action_plan"):
        action_id_to_delete = action_actions.get("action_id_to_delete")
        actions_before = existing_minutes.get(MinutesFields.ACTION_PLAN, [])
        actions = [a for a in actions_before if a["id"] != action_id_to_delete]
        if len(actions_before) == len(actions):
            print(
                f"❌ [エラー] 削除対象のアクションプラン (ID: {action_id_to_delete}) が見つかりません"
            )
        else:
            print(f"✅ [削除完了] アクションプラン ID: {action_id_to_delete}")
        doc_ref.update({MinutesFields.ACTION_PLAN: actions})

    ### **アジェンダの完了処理** ###
    if action_agenda.get("completed_agenda_ids"):
        completed_agenda_ids = action_agenda["completed_agenda_ids"]
        agendas = existing_minutes.get(MinutesFields.AGENDA, [])

        updated = False
        for agenda in agendas:
            if str(agenda["id"]) in completed_agenda_ids and not agenda["completed"]:
                agenda["completed"] = True
                updated = True
                print(
                    f"✅ [完了] アジェンダ ID: {agenda['id']} | {agenda.get('topic')}"
                )

        if updated:
            doc_ref.update({MinutesFields.AGENDA: agendas})


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
