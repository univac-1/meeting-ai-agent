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
    agenda: list[str]
    participants: list[str]
    conversation_history: list[dict]

# 状態の型定義
class GraphState(TypedDict):
    purpose: str
    agenda: list[str]
    participants: list[str]
    conversation_history: list[dict]
    evaluation: str | None
    improvement: str | None

def get_llm():
    """環境変数からAPI Keyを取得してLLMを初期化"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set")
    return ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=api_key)

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
会議の発話履歴: {conversation_history}""")
    ])
    
    model = get_llm()
    
    def evaluate(state: GraphState) -> GraphState:
        messages = prompt.format_messages(
            purpose=state["purpose"],
            agenda=state["agenda"],
            participants=state["participants"],
            conversation_history=state["conversation_history"]
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
    workflow.add_node("evaluate", create_evaluation_node())
    workflow.add_node("improve", create_improvement_node())
    
    # エッジの設定
    workflow.set_entry_point("evaluate")  # 開始ノードを設定
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
        agenda=meeting_input.agenda,
        participants=meeting_input.participants,
        conversation_history=meeting_input.conversation_history,
        evaluation=None,
        improvement=None
    )
    
    # グラフの実行
    result = graph.invoke(initial_state)
    
    return {
        "summary": result["evaluation"],
        "evaluation": result["evaluation"],
        "improvements": result["improvement"]
    } 