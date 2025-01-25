from typing import Dict, TypedDict, Annotated, Sequence
from datetime import datetime
import os

from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from pydantic import BaseModel

# 入力データの型定義
class MeetingInput(BaseModel):
    purpose: str
    agenda: list[str] | None = None
    participants: list[str]
    comment_history: list[dict]

# 状態の型定義
class GraphState(TypedDict):
    purpose: str
    agenda: list[str]
    participants: list[str]
    comment_history: list[dict]
    summary: str | None
    evaluation: str | None
    improvement: str | None

def get_llm():
    """環境変数からAPI KeyとモデルIDを取得してLLMを初期化"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set")
    
    model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")  # デフォルトはgemini-1.5-flash
    return ChatGoogleGenerativeAI(model=model_name, google_api_key=api_key)

# アジェンダ生成ノード
def create_agenda_node():
    prompt = ChatPromptTemplate.from_messages([
        ("human", """あなたは会議のファシリテーターとして、以下の会議の目的に基づいて効果的なアジェンダを作成してください。

会議の目的: {purpose}
参加者: {participants}

アジェンダは以下の点を考慮して作成してください：
1. 会議の目的を達成するために必要なステップ
2. 参加者全員が効果的に議論に参加できる構成
3. 時間配分を考慮した現実的な項目数（3-5項目程度）
4. 具体的な成果物や決定事項の明確化

以下の形式で箇条書きのリストとして提案してください：
- [アジェンダ項目1]
- [アジェンダ項目2]
- [アジェンダ項目3]
...

各アジェンダ項目は、具体的なアクションや目標を示す短い文章にしてください。""")
    ])
    
    model = get_llm()
    
    def generate_agenda(state: GraphState) -> GraphState:
        messages = prompt.format_messages(
            purpose=state["purpose"],
            participants=state["participants"]
        )
        response = model.invoke(messages)
        # 応答からアジェンダのリストを抽出（'-'で始まる行のみを抽出）
        agenda_items = [item.strip('- ') for item in response.content.split('\n') if item.strip().startswith('-')]
        if not agenda_items:  # 箇条書きでない場合は行ごとに分割して最初の3-5行を使用
            agenda_items = [item.strip() for item in response.content.split('\n') if item.strip()][:5]
        state["agenda"] = agenda_items
        return state
    
    return generate_agenda

# 会議要約ノード
def create_summary_node():
    prompt = ChatPromptTemplate.from_messages([
        ("human", """あなたは会議の内容を簡潔に要約する専門家として、以下の情報をもとに会議の内容を要約してください。

要約のポイント：
1. 議論された主要なトピック
2. 参加者から出された重要な意見
3. 決定事項や合意点
4. 未解決の課題

200字程度で簡潔にまとめてください。

会議の目的: {purpose}
アジェンダ: {agenda}
参加者: {participants}
コメント履歴: {conversation_history}""")
    ])
    
    model = get_llm()
    
    def summarize(state: GraphState) -> GraphState:
        messages = prompt.format_messages(
            purpose=state["purpose"],
            agenda=state["agenda"],
            participants=state["participants"],
            conversation_history=state["comment_history"]
        )
        response = model.invoke(messages)
        state["summary"] = response.content
        return state
    
    return summarize

# 会議評価ノード
def create_evaluation_node():
    prompt = ChatPromptTemplate.from_messages([
        ("human", """あなたは会議の評価を行う専門家として、以下の情報をもとに会議の進行状況と内容を評価してください：

評価のポイント：
1. アジェンダに沿った進行ができているか
2. 参加者全員が適切に発言できているか
3. 会議の目的に向かって議論が進んでいるか
4. 時間の使い方は効率的か

具体的な例を挙げながら、改善点も指摘してください。

会議の目的: {purpose}
アジェンダ: {agenda}
参加者: {participants}
コメント履歴: {conversation_history}""")
    ])
    
    model = get_llm()
    
    def evaluate(state: GraphState) -> GraphState:
        messages = prompt.format_messages(
            purpose=state["purpose"],
            agenda=state["agenda"],
            participants=state["participants"],
            conversation_history=state["comment_history"]
        )
        response = model.invoke(messages)
        state["evaluation"] = response.content
        return state
    
    return evaluate

# 会議改善ノード
def create_improvement_node():
    prompt = ChatPromptTemplate.from_messages([
        ("human", """あなたは会議の改善を提案する専門家として、以下の点について具体的な改善案を提案してください：

1. 残りの時間でどのように会議を進行すべきか
2. 参加者の発言を促すためのアドバイス
3. 会議の目的達成のための具体的なアクション

提案は実践的で具体的なものにしてください。

会議の評価結果: {evaluation}
会議の目的: {purpose}
アジェンダ: {agenda}
参加者: {participants}""")
    ])
    
    model = get_llm()
    
    def improve(state: GraphState) -> GraphState:
        messages = prompt.format_messages(
            evaluation=state["evaluation"],
            purpose=state["purpose"],
            agenda=state["agenda"],
            participants=state["participants"]
        )
        response = model.invoke(messages)
        state["improvement"] = response.content
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

# グラフの使用例
def process_meeting_feedback(meeting_input: MeetingInput) -> Dict:
    graph = create_meeting_feedback_graph()
    
    # 初期状態の設定
    initial_state = GraphState(
        purpose=meeting_input.purpose,
        agenda=meeting_input.agenda or [],  # Noneの場合は空リストを設定
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