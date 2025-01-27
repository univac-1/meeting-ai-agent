from typing import Dict, Optional, List
from typing_extensions import TypedDict
from datetime import datetime
import os
import google.generativeai as genai
from langgraph.graph import StateGraph, END, START
from pydantic import BaseModel
import json
from config import Config

# 入力データの型定義
class MeetingInput(BaseModel):
    purpose: str
    agenda: Optional[List[str]] = None
    participants: List[str]
    comment_history: List[Dict]

# 評価結果の型定義
class EvaluationResult(TypedDict):
    engagement: str
    concreteness: str
    direction: str

# 状態の型定義
class GraphState(TypedDict):
    purpose: str
    agenda: List[str]
    participants: List[str]
    comment_history: List[Dict]
    facilitator_message: Optional[str]
    summary: Optional[str]
    evaluation: Optional[EvaluationResult]

# エージェントの処理結果詳細
class DetailResponse(TypedDict):
    summary: Optional[str]
    evaluation: Optional[str]
    agenda: Optional[List[str]]

# エージェントの処理結果
class ProcessMeetingFeedbackResponse(TypedDict):
    message: str
    detail: DetailResponse

# LLMのレスポンス型定義
class AgentResponse(TypedDict):
    agenda: List[str]
    summary: str
    evaluation: Dict[str, str]
    message: str

# LLMのレスポンススキーマ定義
AGENDA_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "アジェンダ": {
            "type": "array",
            "description": "会議のアジェンダ項目のリスト",
            "items": {
                "type": "string"
            }
        }
    },
    "required": ["アジェンダ"]
}

SUMMARY_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "要約": {
            "type": "string",
            "description": "会議の進行状況の要約"
        }
    },
    "required": ["要約"]
}

EVALUATION_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "参加者の関与度": {
            "type": "string",
            "description": "参加者の関与度に関する評価"
        },
        "議論の具体性": {
            "type": "string",
            "description": "議論の具体性に関する評価"
        },
        "議論の方向性": {
            "type": "string",
            "description": "議論の方向性に関する評価"
        }
    },
    "required": ["参加者の関与度", "議論の具体性", "議論の方向性"]
}

FACILITATOR_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "次の発言": {
            "type": "string",
            "description": "ファシリテータとしての次の発言内容"
        }
    },
    "required": ["次の発言"]
}

def init_gemini(system_instruction: str = None):
    """Gemini APIの初期化"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set")
    
    genai.configure(api_key=api_key)
    model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash-002")
    
    if system_instruction:
        return genai.GenerativeModel(
            model_name,
            system_instruction=[system_instruction]
        )
    return genai.GenerativeModel(model_name)

# アジェンダ生成ノード
def create_agenda_node():
    system_prompt = f"""あなたは会議の目的に基づいてアジェンダを作成する専門のAIです。
与えられた入力を踏まえた上で、会議の目的を達成するために必要なステップをアジェンダとして作成してください。

アジェンダのポイント：
1. 会議の目的を達成するために必要なステップ
2. 参加者全員が効果的に議論に参加できる構成
3. 時間配分を考慮した現実的な項目数（3-5項目程度）
4. 具体的な成果物や決定事項の明確化

入力：
- 目的：会議の目的
- 参加者：会議の参加者
"""
    
    model = init_gemini(system_prompt)
    
    def generate_agenda(state: GraphState) -> GraphState:
        prompt = {
            "目的": state["purpose"],
            "参加者": state["participants"]
        }

        response = model.generate_content(
            str(prompt),
            generation_config=genai.GenerationConfig(
                temperature=0.7,
                candidate_count=1,
                response_mime_type="application/json",
                response_schema=AGENDA_RESPONSE_SCHEMA
            )
        )

        try:
            result = json.loads(response.text)
            state["agenda"] = result["アジェンダ"]
            return state
        except Exception as e:
            print(f"Error processing agenda: {e}")
            state["agenda"] = []
            return state
    
    return generate_agenda

# 会議要約ノード
def create_summary_node():
    system_prompt = """あなたは進行途中の会議の状況を簡潔に要約する専門のAIです。
与えられた入力を踏まえた上で、会議の状況を要約してください

要約のポイント：
1. 議論された主要なトピック
2. 参加者から出された重要な意見
3. 決定事項や合意点
4. 未解決の課題
5. 会議は進行途中であるため、必ずしもすべてのアジェンダを網羅しているとは限らない
6. AIの発言内容は除外する

入力：
- 目的：会議の目的
- アジェンダ：会議のアジェンダ
- 参加者：会議の参加者
- 発言履歴：会議の発言履歴
"""
    
    model = init_gemini(system_prompt)
    
    def summarize(state: GraphState) -> GraphState:
        prompt = {
            "目的": state["purpose"],
            "アジェンダ": state["agenda"],
            "参加者": state["participants"],
            "発言履歴": state["comment_history"]
        }

        response = model.generate_content(
            str(prompt),
            generation_config=genai.GenerationConfig(
                temperature=0.3,
                candidate_count=1,
                response_mime_type="application/json",
                response_schema=SUMMARY_RESPONSE_SCHEMA
            )
        )

        try:
            result = json.loads(response.text)
            state["summary"] = result["要約"]
            return state
        except Exception as e:
            print(f"Error processing summary: {e}")
            state["summary"] = ""
            return state
    
    return summarize

# 会議評価ノード
def create_evaluation_node():
    system_prompt = """あなたは会議の進行状況を評価する専門のAIです。
以下の観点から会議の状況を評価してください：

1. 参加者の関与度
   - 発言の偏りはないか
   - 全員が議論に参加できているか
   - 建設的な意見交換ができているか

2. 議論の具体性
   - 抽象的な発言が多くないか
   - 具体的な提案や例示があるか
   - 参加者間で認識の共有ができているか

3. 議論の方向性
   - 議論が脱線していないか
   - 建設的な雰囲気が保たれているか
   - 次のステップが明確か

入力：
- 目的：会議の目的
- アジェンダ：会議のアジェンダ
- 参加者：会議の参加者
- 発言履歴：会議の発言履歴
"""

    model = init_gemini(system_prompt)
    
    def evaluate(state: GraphState) -> GraphState:
        prompt = {
            "目的": state["purpose"],
            "アジェンダ": state["agenda"],
            "参加者": state["participants"],
            "発言履歴": state["comment_history"]
        }

        response = model.generate_content(
            str(prompt),
            generation_config=genai.GenerationConfig(
                temperature=0.3,
                candidate_count=1,
                response_mime_type="application/json",
                response_schema=EVALUATION_RESPONSE_SCHEMA
            )
        )

        try:
            result = json.loads(response.text)
            state["evaluation"] = {
                "engagement": result["参加者の関与度"],
                "concreteness": result["議論の具体性"],
                "direction": result["議論の方向性"]
            }
            return state
        except Exception as e:
            print(f"Error processing evaluation: {e}")
            state["evaluation"] = {
                "engagement": "",
                "concreteness": "",
                "direction": ""
            }
            return state
    
    return evaluate

# ファシリテータノード
def create_facilitator_node():
    system_prompt = f"""あなたは会議のファシリテータAIです。
以下の評価結果に基づいて、適切な介入を行ってください：

1. 参加者の関与度が低い場合
   - 発言の少ない参加者に意見を求める
   - 参加者の発言を肯定的に受け止める
   - 全員が参加できる話題を提供する

2. 議論の具体性が低い場合
   - 抽象的な発言を具体化する
   - 具体的な例を示す
   - 参加者間の認識の違いを解消する

3. 議論の方向性がずれている場合
   - 議論を目的に沿った方向に戻す
   - 建設的な雰囲気を取り戻す
   - 次のステップを提案する

発言のポイント：
1. 「〇〇さん」と名前を呼んで話しかける
2. 「〜ということですよね？」と確認を取る
3. 「たとえば、〜」と具体例を示す
4. 「どう思いますか？」と他の参加者に意見を求める
5. 常に丁寧で親しみやすい口調を維持する

入力：
- 目的：会議の目的
- アジェンダ：会議のアジェンダ
- 参加者：会議の参加者
- 発言履歴：会議の発言履歴
- 評価結果：会議の評価結果

出力：
- 評価結果に基づいて、最も優先度の高い課題に対応する発言をしてください
- 会議の目的やアジェンダに沿った具体例を含めてください
- 最後に必ず他の参加者に意見を求めてください
- 説明的な内容は避け、自然な会話の流れを意識してください
"""
    
    model = init_gemini(system_prompt)
    
    def facilitate(state: GraphState) -> GraphState:
        prompt = {
            "目的": state["purpose"],
            "アジェンダ": state["agenda"],
            "参加者": state["participants"],
            "発言履歴": state["comment_history"],
            "評価結果": state["evaluation"]
        }

        response = model.generate_content(
            str(prompt),
            generation_config=genai.GenerationConfig(
                temperature=0.7,
                candidate_count=1,
                response_mime_type="application/json",
                response_schema=FACILITATOR_RESPONSE_SCHEMA
            )
        )

        try:
            result = json.loads(response.text)
            state["facilitator_message"] = result["次の発言"]
            return state
        except Exception as e:
            print(f"Error processing facilitator response: {e}")
            state["facilitator_message"] = ""
            return state
    
    return facilitate


def create_meeting_feedback_graph():
    """会議フィードバックのグラフを作成する"""
    # グラフの作成
    workflow = StateGraph(GraphState)
    
    # ノードの追加
    workflow.add_node("create_agenda", create_agenda_node())
    workflow.add_node("summarize", create_summary_node())
    workflow.add_node("evaluate", create_evaluation_node())
    workflow.add_node("facilitate", create_facilitator_node())
    
    # 条件分岐の関数
    def should_create_agenda(state: GraphState) -> Dict[str, str]:
        # アジェンダが空または未設定の場合はアジェンダ生成ノードへ
        if not state.get("agenda"):
            return {"next": "create_agenda"}
        return {"next": "summarize"}
    
    # エッジの設定
    workflow.add_node("router", should_create_agenda)
    workflow.add_edge(START, "router")
    workflow.add_conditional_edges(
        "router",
        lambda x: x["next"],
        {
            "create_agenda": "create_agenda",
            "summarize": "summarize"
        }
    )
    workflow.add_edge("create_agenda", END)
    workflow.add_edge("summarize", "evaluate")
    workflow.add_edge("evaluate", "facilitate")
    workflow.add_edge("facilitate", END)
    
    # 実行可能なグラフの取得
    return workflow.compile()

def process_meeting_feedback(meeting_input: MeetingInput) -> ProcessMeetingFeedbackResponse:
    """会議の状態を受け取り、フィードバックを生成"""
    # 初期状態の設定
    state = GraphState(
        purpose=meeting_input.purpose,
        agenda=meeting_input.agenda if meeting_input.agenda else [],
        participants=meeting_input.participants,
        comment_history=meeting_input.comment_history,
        facilitator_message=None,
        summary=None,
        evaluation=None,
    )

    # グラフの実行
    graph = create_meeting_feedback_graph()
    final_state = graph.invoke(state)

    # アジェンダ生成の場合
    if not meeting_input.agenda:
        return {
            "message": "アジェンダを作成しました。",
            "detail": {
                "agenda": final_state.get("agenda", [])
            }
        }

    # 通常のフィードバックの場合
    return {
        "message": final_state.get("facilitator_message", ""),
        "detail": {
            "summary": final_state.get("summary", ""),
            "evaluation": final_state.get("evaluation", {})
        }
    }


