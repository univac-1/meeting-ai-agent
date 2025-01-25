from typing import Dict, List
from langgraph.graph import Graph, StateGraph
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
import re

class ConversationState:
    def __init__(self):
        self.messages: List[BaseMessage] = []
        self.next_step: str = "agent"
        
    def add_message(self, message: BaseMessage):
        self.messages.append(message)

def create_chat_model():
    return ChatGoogleGenerativeAI(
        model="gemini-pro",
        temperature=0.7,
        convert_system_message_to_human=True
    )

def parse_message(text: str) -> tuple[str, str]:
    """ユーザー名と発言内容を抽出する"""
    pattern = r'(.+?)「(.+?)」'
    match = re.match(pattern, text)
    if match:
        return match.group(1), match.group(2)
    return None, None

def create_system_prompt() -> str:
    return """あなたは対立する人々の間で仲裁を行う調停者です。
以下の原則に従って行動してください：

1. 各ユーザーの主張を客観的に分析し、論点を整理してください
2. 対立している当事者それぞれの立場や感情を理解し、認めてください
3. 建設的な解決策を提案し、和解への道筋を示してください
4. 中立的な立場を保ちながら、公平な提言を行ってください
5. 必要に応じて、誤解や認識の違いを指摘し、相互理解を促してください

出力形式：
AI「<提言内容>」
"""

def agent(state: ConversationState) -> Dict:
    chat = create_chat_model()
    
    # システムプロンプトを追加
    if not state.messages:
        state.add_message(SystemMessage(content=create_system_prompt()))
    
    response = chat.invoke(state.messages)
    
    # 応答形式を整形
    content = response.content
    if not content.startswith('AI「'):
        content = f'AI「{content}」'
    
    state.add_message(AIMessage(content=content))
    
    return {"messages": state.messages, "next_step": "end"}

def create_conversation_graph() -> Graph:
    workflow = StateGraph(ConversationState)
    
    workflow.add_node("agent", agent)
    workflow.set_entry_point("agent")
    workflow.add_edge("agent", "end")
    
    return workflow.compile()

def handle_conversation(user_input: str) -> List[str]:
    graph = create_conversation_graph()
    state = ConversationState()
    
    # 入力メッセージをパースしてユーザー名と内容を抽出
    username, content = parse_message(user_input)
    if username and content:
        state.add_message(HumanMessage(content=user_input))
    else:
        return ["メッセージの形式が正しくありません。'ユーザー名「メッセージ内容」'の形式で入力してください。"]
    
    result = graph.invoke(state)
    
    # AIの応答のみを返す
    messages = result["messages"]
    ai_messages = [msg.content for msg in messages if isinstance(msg, AIMessage)]
    return ai_messages 