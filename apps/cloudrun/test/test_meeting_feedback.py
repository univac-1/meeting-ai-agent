from cloudrun.agent.feedback_agent import process_meeting_feedback, MeetingInput
import json
import os

def _test_with_agenda():
    """既存のアジェンダがある場合のテスト"""
    test_data = MeetingInput(
        purpose="プロダクトのアイデアを決める",
        agenda=[
            "参加者からアイデアを募る",
            "参加者同士でアイデアを評価",
            "最も評価のよいものに決定"
        ],
        participants=["ごん", "ぴとー", "ごれいぬ"],
        comment_history=[
            {"speaker": "ごん", "message": "ぼくは事務手続きの処理フローを可視化するツールを作りたい"},
            {"speaker": "ぴとー", "message": "それってネットで検索すればよくない?chatbotもある気がするけど"},
            {"speaker": "ごん", "message": "パスポートをとったときの話だけど、必要なフローを網羅するのに横断的にサイト検索しないといけないのは大変だったよ。"},
            {"speaker": "ぴとー", "message": "ごめん、なにいってるかよくわかんない。次"}
        ]
    )
    
    print("\n=== アジェンダありのケース ===")
    result = process_meeting_feedback(test_data)
    print("\n=== 結果 ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))

def _test_without_agenda():
    """アジェンダがない場合のテスト"""
    test_data = MeetingInput(
        purpose="プロダクトのアイデアを決める",
        agenda=None,
        participants=["ごん", "ぴとー", "ごれいぬ"],
        comment_history=[
            {"speaker": "ごん", "message": "ぼくは事務手続きの処理フローを可視化するツールを作りたい"},
            {"speaker": "ぴとー", "message": "それってネットで検索すればよくない?chatbotもある気がするけど"},
            {"speaker": "ごん", "message": "パスポートをとったときの話だけど、必要なフローを網羅するのに横断的にサイト検索しないといけないのは大変だったよ。"},
            {"speaker": "ぴとー", "message": "ごめん、なにいってるかよくわかんない。次"}
        ]
    )
    
    print("\n=== アジェンダなしのケース ===")
    print("会議の目的:", test_data.purpose)
    print("参加者:", ", ".join(test_data.participants))
    
    result = process_meeting_feedback(test_data)
    print("\n=== 結果 ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))

def test_with_file_data():
    """テストデータファイルを使用したテスト"""
    # 入力データの読み込み
    input_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "test_agent_1_input.json")
    with open(input_file, "r", encoding="utf-8") as f:
        input_data = json.load(f)
    
    # 期待値の読み込み
    expected_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "test_agent_1_expected.json")
    with open(expected_file, "r", encoding="utf-8") as f:
        expected_data = json.load(f)
    
    # MeetingInputの作成
    meeting_input = MeetingInput(
        purpose=input_data["purpose"],
        agenda=input_data.get("agenda"),
        participants=input_data["participants"],
        comment_history=input_data["comment_history"]
    )
    
    print("\n=== テストデータファイルを使用したテスト ===")
    print("入力データ:")
    print(json.dumps(input_data, ensure_ascii=False, indent=2))
    
    # テスト実行
    result = process_meeting_feedback(meeting_input)
    print("\n=== 結果 ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    print("\n=== 期待値との比較 ===")
    print("期待値:")
    print(json.dumps(expected_data, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    # _test_with_agenda()
    # _test_without_agenda()
    test_with_file_data()