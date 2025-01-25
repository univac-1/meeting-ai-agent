from meeting_feedback_graph import process_meeting_feedback, MeetingInput

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
    print("=== 既存のアジェンダ ===")
    print("\n".join(f"- {item}" for item in result["agenda"]))
    
    if "summary" in result:
        print("\n=== 会議の要約 ===")
        print(result["summary"])
    
    if "evaluation" in result:
        print("\n=== 会議の評価 ===")
        print(result["evaluation"])
    
    if "improvements" in result:
        print("\n=== 改善提案 ===")
        print(result["improvements"])

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
    if "agenda" in result:
        print("\n=== 生成されたアジェンダ ===")
        print("\n".join(f"- {item}" for item in result["agenda"]))

if __name__ == "__main__":
    # _test_with_agenda()
    _test_without_agenda()