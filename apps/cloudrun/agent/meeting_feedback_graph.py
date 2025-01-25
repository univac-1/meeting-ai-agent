from typing import Dict, Optional, List
from typing_extensions import TypedDict
from datetime import datetime
import os
import google.generativeai as genai
from langgraph.graph import StateGraph, END
from pydantic import BaseModel
import json

# 入力データの型定義
class MeetingInput(BaseModel):
    purpose: str
    agenda: Optional[List[str]] = None
    participants: List[str]
    comment_history: List[Dict]

# 状態の型定義
class GraphState(TypedDict):
    purpose: str
    agenda: List[str]
    participants: List[str]
    comment_history: List[Dict]
    summary: Optional[str]
    evaluation: Optional[str]
    improvement: Optional[str]

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
    system_prompt = """あなたは会議のファシリテーターとして、会議の目的に基づいて効果的なアジェンダを作成します。
以下の点を考慮してアジェンダを作成してください：
1. 会議の目的を達成するために必要なステップ
2. 参加者全員が効果的に議論に参加できる構成
3. 時間配分を考慮した現実的な項目数（3-5項目程度）
4. 具体的な成果物や決定事項の明確化"""
    
    model = init_gemini(system_prompt)
    print("before generate_agenda")
    
    def generate_agenda(state: GraphState) -> GraphState:
        prompt = {
            "purpose": state["purpose"],
            "participants": state["participants"]
        }

        print(prompt)
        response = model.generate_content(
            str(prompt),
            generation_config=genai.GenerationConfig(
                temperature=0.7,
                candidate_count=1,
                response_mime_type="application/json",
                response_schema=AgendaResponse
            )
        )
        print(response.text)

        try:
            result = json.loads(response.text)
            state["agenda"] = result["agenda"]
            return state
        except Exception as e:
            print(f"Error processing agenda: {e}")
            state["agenda"] = []
            return state
    
    return generate_agenda

# 会議要約ノード
def create_summary_node():
    system_prompt = """あなたは会議の内容を簡潔に要約する専門家です。
以下のポイントに注目して要約を作成してください：
1. 議論された主要なトピック
2. 参加者から出された重要な意見
3. 決定事項や合意点
4. 未解決の課題"""
    
    model = init_gemini(system_prompt)
    
    def summarize(state: GraphState) -> GraphState:
        prompt = {
            "purpose": state["purpose"],
            "agenda": state["agenda"],
            "participants": state["participants"],
            "comment_history": state["comment_history"]
        }

        response = model.generate_content(
            str(prompt),
            generation_config=genai.GenerationConfig(
                temperature=0.3,
                candidate_count=1,
                response_mime_type="application/json",
                response_schema=SummaryResponse
            )
        )

        try:
            result = json.loads(response.text)
            state["summary"] = result["summary"]
            return state
        except Exception as e:
            print(f"Error processing summary: {e}")
            state["summary"] = ""
            return state
    
    return summarize

# 会議評価ノード
def create_evaluation_node():
    system_prompt = """あなたは会議の評価を行う専門家です。
以下のポイントについて評価してください：
1. アジェンダに沿った進行ができているか
2. 参加者全員が適切に発言できているか
3. 会議の目的に向かって議論が進んでいるか
4. 時間の使い方は効率的か"""
    
    model = init_gemini(system_prompt)
    
    def evaluate(state: GraphState) -> GraphState:
        prompt = {
            "purpose": state["purpose"],
            "agenda": state["agenda"],
            "participants": state["participants"],
            "comment_history": state["comment_history"]
        }

        response = model.generate_content(
            str(prompt),
            generation_config=genai.GenerationConfig(
                temperature=0.3,
                candidate_count=1,
                response_mime_type="application/json",
                response_schema=EvaluationResponse
            )
        )

        try:
            result = json.loads(response.text)
            state["evaluation"] = result["evaluation"]
            return state
        except Exception as e:
            print(f"Error processing evaluation: {e}")
            state["evaluation"] = ""
            return state
    
    return evaluate

# 会議改善ノード
def create_improvement_node():
    system_prompt = """あなたは会議の改善を提案する専門家です。
以下の点について具体的な改善案を提案してください：
1. 残りの時間でどのように会議を進行すべきか
2. 参加者の発言を促すためのアドバイス
3. 会議の目的達成のための具体的なアクション"""
    
    model = init_gemini(system_prompt)
    
    def improve(state: GraphState) -> GraphState:
        prompt = {
            "evaluation": state["evaluation"],
            "purpose": state["purpose"],
            "agenda": state["agenda"],
            "participants": state["participants"]
        }

        response = model.generate_content(
            str(prompt),
            generation_config=genai.GenerationConfig(
                temperature=0.3,
                candidate_count=1,
                response_mime_type="application/json",
                response_schema=ImprovementResponse
            )
        )

        try:
            result = json.loads(response.text)
            state["improvement"] = result["improvements"]
            return state
        except Exception as e:
            print(f"Error processing improvements: {e}")
            state["improvement"] = ""
            return state
    
    return improve

def create_meeting_feedback_graph():
    # グラフの作成
    workflow = StateGraph(GraphState)
    
    # ノードの追加
    workflow.add_node("generate_agenda", create_agenda_node())
    workflow.add_node("summarize", create_summary_node())
    workflow.add_node("evaluate", create_evaluation_node())
    workflow.add_node("improve", create_improvement_node())
    
    # 条件付きエッジの設定
    def should_generate_agenda(state: GraphState) -> Dict[str, str]:
        # アジェンダが空または未設定の場合はアジェンダ生成ノードへ
        if not state.get("agenda"):
            return {"next": "generate_agenda"}
        return {"next": "summarize"}
    
    # エッジの設定
    workflow.add_node("router", should_generate_agenda)  # 条件分岐ノードを追加
    workflow.set_entry_point("router")  # エントリーポイントを設定
    
    # ルーティングの設定
    workflow.add_conditional_edges(
        "router",
        lambda x: x["next"],
        {
            "generate_agenda": "generate_agenda",
            "summarize": "summarize"
        }
    )
    # アジェンダ生成後はそこで終了、それ以外は通常のフローへ
    workflow.add_edge("generate_agenda", END)
    workflow.add_edge("summarize", "evaluate")
    workflow.add_edge("evaluate", "improve")
    workflow.add_edge("improve", END)
    
    # 実行可能なグラフの取得
    return workflow.compile()

def process_meeting_feedback(meeting_input: MeetingInput) -> Dict:
    """会議フィードバックの処理"""
    graph = create_meeting_feedback_graph()
    
    # 初期状態の設定
    initial_state = GraphState(
        purpose=meeting_input.purpose,
        agenda=meeting_input.agenda or [],
        participants=meeting_input.participants,
        comment_history=meeting_input.comment_history,
        summary=None,
        evaluation=None,
        improvement=None
    )
    
    # グラフの実行
    result = graph.invoke(initial_state)
    
    # アジェンダ生成の場合は、アジェンダのみを返す
    if not meeting_input.agenda:
        return {
            "agenda": result["agenda"]
        }
    
    # 通常のフィードバックの場合は全ての情報を返す
    return {
        "agenda": result["agenda"],
        "summary": result["summary"],
        "evaluation": result["evaluation"],
        "improvements": result["improvement"]
    }

class AgendaResponse(TypedDict):
    agenda: list[str]

class SummaryResponse(TypedDict):
    summary: str

class EvaluationResponse(TypedDict):
    evaluation: str

class ImprovementResponse(TypedDict):
    improvements: str 