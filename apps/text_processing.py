import google.generativeai as genai
from typing import List

# Gemini APIの設定
genai.configure(api_key="GEMINI_API_KEY")

def translate_to_natural_japanese(text: str) -> str:
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"以下のテキストを自然な日本語に変換してください：\n{text}"
    
    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            temperature=0.3
        )
    )
    return response.text

def summarize_text(text: str) -> str:
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"以下のテキストを要約してください：\n{text}"
    
    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            temperature=0.3
        )
    )
    return response.text

def process_text(input_text: str) -> List[str]:
    # 結果を格納するリスト
    results = [input_text]
    
    # ステップ1: 日本語に変換
    translated = translate_to_natural_japanese(input_text)
    results.append(translated)
    
    # ステップ2: 要約
    summary = summarize_text(translated)
    results.append(summary)
    
    return results

if __name__ == "__main__":
    input_text = "AI tech is rapidly evolving, bringing both opportunities and challenges."
    results = process_text(input_text)
    
    print("元のテキスト:", results[0])
    print("日本語変換:", results[1])
    print("要約:", results[2]) 