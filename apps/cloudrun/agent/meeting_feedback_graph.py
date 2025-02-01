from typing import Dict, Optional, List
from typing_extensions import TypedDict
from datetime import datetime
import os
import google.generativeai as genai
from langgraph.graph import StateGraph, END
from pydantic import BaseModel
import json
from config import Config

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
    comment: Optional[str]
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
                response_schema=AgendaResponse
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
                response_schema=SummaryResponse
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
    system_prompt = """あなたは進行途中の会議の評価を行う専門のAIです。
与えられた入力を踏まえた上で、会議の評価を行ってください

評価の観点：
1. 会議の目的から脱線していないか
2. 発言者が偏っていないか
3. 発言者の意図が正確に伝わっているか
4. 会議は進行途中であるため、必ずしもすべてのアジェンダを網羅しているとは限らない
5. AIの発言内容は除外する

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
                response_schema=EvaluationResponse
            )
        )

        try:
            result = json.loads(response.text)
            state["evaluation"] = result["評価"]
            return state
        except Exception as e:
            print(f"Error processing evaluation: {e}")
            state["evaluation"] = ""
            return state
    
    return evaluate

# 会議改善ノード
def create_improvement_node():
    system_prompt = """あなたは進行途中の会議を改善する専門のAIです。
以下の入力を踏まえた上で、会議の残り時間で出来る範囲で会議を改善してください。

改善のポイント：
1. 時間配分を考慮した現実的な項目数（3項目以下）にする
2. 言語化能力の不足など、参加者の能力に依存するような課題はAI自身で補うようにする
3. 改善は、残りの会議時間でできるものに限る
4. AIの発言内容は除外する

入力：
- 目的：会議の目的
- アジェンダ：会議のアジェンダ
- 参加者：会議の参加者
- 評価：会議の評価
"""
    
    model = init_gemini(system_prompt)
    
    def improve(state: GraphState) -> GraphState:
        prompt = {
            "目的": state["purpose"],
            "アジェンダ": state["agenda"],
            "参加者": state["participants"],
            "評価": state["evaluation"]
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
            state["improvement"] = result["改善案"]
            return state
        except Exception as e:
            print(f"Error processing improvements: {e}")
            state["improvement"] = ""
            return state
    
    return improve

def create_comment_node():
    system_prompt = """あなたは進行途中の会議で人間を応援するAIです。
会議の評価と改善案を踏まえて、端的に応援コメントをしてください。

コメントのポイント：
1. 会議は進行途中であるため、必ずしもすべてのアジェンダを網羅しているとは限らない
2. コメントは1文程度の簡潔なもの
3. 残りの会議を雰囲気よく進めやすくなるようなポップな表現にする

入力：
- 評価：会議の評価
- 改善案：会議の改善案
"""
    
    model = init_gemini(system_prompt)
    
    def comment(state: GraphState) -> GraphState:
        prompt = {
            "評価": state["evaluation"],
            "改善案": state["improvement"]
        }

        response = model.generate_content(
            str(prompt),
            generation_config=genai.GenerationConfig(
                temperature=0.3,
                candidate_count=1,
                response_mime_type="application/json",
                response_schema=CommentResponse
            )
        )

        try:
            result = json.loads(response.text)
            state["comment"] = result["コメント"]
            return state
        except Exception as e:
            print(f"Error processing comment: {e}")
            state["comment"] = ""
            return state
    
    return comment

def create_meeting_feedback_graph():
    # グラフの作成
    workflow = StateGraph(GraphState)
    
    # ノードの追加
    workflow.add_node("generate_agenda", create_agenda_node())
    workflow.add_node("summarize", create_summary_node())
    workflow.add_node("evaluate", create_evaluation_node())
    workflow.add_node("improve", create_improvement_node())
    workflow.add_node("generate_comment", create_comment_node())
    
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
    workflow.add_edge("improve", "generate_comment")
    workflow.add_edge("generate_comment", END)
    
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
        comment=None,
        summary=None,
        evaluation=None,
        improvement=None
    )
    
    # グラフの実行
    result = graph.invoke(initial_state)
    
    # アジェンダ生成の場合は、アジェンダのみを返す
    if not meeting_input.agenda:
        return {
            "message": "アジェンダを作成しました。",
            "detail": AgendaResponse(
                agenda=result["agenda"]
            )
        }
    
    # 通常のフィードバックの場合は新しい構造で返す
    return {
        "message": result["comment"],
        "detail": DetailResponse(
            summary=result["summary"],
            evaluation=result["evaluation"],
            improvement=result["improvement"]
        )
    }

class AgendaResponse(TypedDict):
    アジェンダ: list[str]

class SummaryResponse(TypedDict):
    要約: str

class EvaluationResponse(TypedDict):
    評価: str

class ImprovementResponse(TypedDict):
    改善案: str

class CommentResponse(TypedDict):
    コメント: str

class DetailResponse(TypedDict):
    要約: str
    評価: str
    改善案: str 