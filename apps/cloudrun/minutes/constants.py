# Firestore フィールドキー
class MinutesFields:
    AGENDA = "agenda"  # アジェンダのリスト
    DECISIONS = "decisions"  # 決定事項のリスト
    ACTION_PLAN = "action_plan"  # アクションプランのリスト


class ActionPlanFields:
    TASK = "task"  # タスクの内容
    ASSIGNED_TO = "assigned_to"  # 担当者
    DUE_DATE = "due_date"  # 期限
