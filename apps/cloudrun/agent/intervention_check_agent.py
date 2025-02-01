from typing import Optional, List, Tuple, TypedDict
from datetime import datetime
import json
import os
import google.generativeai as genai
from models import MeetingInput, Message
from config import Config

SYSTEM_PROMPT = """あなたは会議のファシリテータとして、会議の進行状況を監視し、介入が必要かどうかを判断します。
与えられた入力を踏まえた上で、介入の必要性を判断してください。ただし、介入は最小限としたいため、参加者のスタンスが不明なうちは介入しないでください。
介入の判断基準：

1. 参加者だけでは解決が難しい状況にあるか
   - 参加者が自力で軌道修正を試みたが失敗している
   - 参加者に軌道修正を試みる兆しがない
   - 意見の対立が深まる一方で、収束の兆しがない

2. 時間管理の観点
   - 予定時間の半分以上を同じ議題で費やしている
   - 残り時間に対して未討議の議題が多すぎる

入力：
- 目的：会議の目的
- アジェンダ：会議のアジェンダ
- 参加者：会議の参加者
- 発言履歴：会議の発言履歴"""

def _init_gemini():
    """Gemini APIの初期化"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set")
    
    genai.configure(api_key=api_key)
    model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash-002")
    
    return genai.GenerativeModel(
        model_name,
        system_instruction=[SYSTEM_PROMPT]
    )

# Geminiの設定
model = _init_gemini()

class InterventionCheckResponse(TypedDict):
    """介入判定の応答を表す型"""
    intervention_needed: bool
    reason: Optional[str]

RESPONSE_SCHEME = {
    "type": "object",
    "properties": {
        "intervention_needed": {
            "type": "boolean",
            "description": "介入が必要かどうかの判断結果"
        },
        "reason": {
            "type": "string",
            "description": "判断の理由"
        }
    },
    "required": ["intervention_needed", "reason"]
}

def should_intervene(meeting_input: MeetingInput) -> Tuple[bool, str]:
    """
    会議の状態から介入が必要かどうかを判定する
    
    Args:
        meeting_input: 会議の情報（目的、アジェンダ、参加者、会話履歴、開始・終了時刻）
        
    Returns:
        Tuple[bool, str]: (介入が必要かどうか, 判断の理由)
            - 介入が必要な場合は (True, 理由の文字列)
            - 介入が不要な場合は (False, 理由の文字列)
    """
    try:
        # プロンプトを準備
        prompt = {
            "目的": meeting_input.get("purpose"),
            "アジェンダ": meeting_input.get("agenda"),
            "参加者": meeting_input.get("participants"),
            "発言履歴": meeting_input.get("comment_history")
        }
        
        # LLMで介入判定
        response = model.generate_content(
            str(prompt),
            generation_config=genai.GenerationConfig(
                temperature=0.1,
                candidate_count=1,
                response_mime_type="application/json",
                response_schema=RESPONSE_SCHEME
            ),
        )
        
        if not response or not response.text:
            return False, None
        
        # JSONレスポンスをパース
        result = json.loads(response.text)
        return result.get("intervention_needed", False), result.get("reason")
        
    except Exception as e:
        print(f"Error in intervention check: {e}")
        return False, None