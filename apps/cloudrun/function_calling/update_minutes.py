import vertexai
from config import Config
from vertexai.preview.generative_models import (
    FunctionDeclaration,
    GenerativeModel,
    Tool,
    ToolConfig,
)


def update_agenda(full_message: str) -> dict:
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

    tool = Tool(function_declarations=[determine_update_agenda_completion])

    model = GenerativeModel(
        "gemini-1.5-flash-002",
        tools=[tool],
        tool_config=ToolConfig(
            function_calling_config=ToolConfig.FunctionCallingConfig(
                mode=ToolConfig.FunctionCallingConfig.Mode.ANY
            )
        ),
    )
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
    return agenda_update


def update_decision(full_message: str) -> dict:
    vertexai.init(project=Config.PROJECT_ID, location="europe-west4")
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

    tool = Tool(function_declarations=[determine_update_decision])
    model = GenerativeModel(
        "gemini-1.5-flash-002",
        tools=[tool],
        tool_config=ToolConfig(
            function_calling_config=ToolConfig.FunctionCallingConfig(
                mode=ToolConfig.FunctionCallingConfig.Mode.ANY
            )
        ),
    )
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

    return decisions_update


def update_action_plan(full_message: str) -> dict:
    vertexai.init(project=Config.PROJECT_ID, location="us-central1")
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

    tool = Tool(function_declarations=[determine_update_action_plan])
    model = GenerativeModel(
        "gemini-1.5-flash-002",
        tools=[tool],
        tool_config=ToolConfig(
            function_calling_config=ToolConfig.FunctionCallingConfig(
                mode=ToolConfig.FunctionCallingConfig.Mode.ANY
            )
        ),
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
    return actions_update
