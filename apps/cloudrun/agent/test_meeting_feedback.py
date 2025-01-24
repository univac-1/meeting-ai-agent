from meeting_feedback_graph import process_meeting_feedback, MeetingInput

# テストデータの作成
test_data = MeetingInput(
    purpose="プロダクトのアイデアを決める",
    agenda=[
        "参加者からアイデアを募る",
        "参加者同士でアイデアを評価",
        "最も評価のよいものに決定"
    ],
    participants=["ごん", "ぴとー", "ごれいぬ"],
    conversation_history=[
        {"speaker": "ごん", "message": "ぼくは事務手続きの処理フローを可視化するツールを作りたい"},
        {"speaker": "ぴとー", "message": "それってネットで検索すればよくない?chatbotもある気がするけど"},
        {"speaker": "ごん", "message": "パスポートをとったときの話だけど、必要なフローを網羅するのに横断的にサイト検索しないといけないのは大変だったよ。"},
        {"speaker": "ぴとー", "message": "ごめん、なにいってるかよくわかんない。次"}
    ]
)

# フィードバックの実行
result = process_meeting_feedback(test_data)

# 結果の表示
print("=== 会議評価 ===")
print(result["evaluation"])
print("\n=== 改善提案 ===")
print(result["improvements"]) 