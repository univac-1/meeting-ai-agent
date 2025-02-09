# meeting-ai-agent
会議AIエージェントのアプリケーション

## 概要
このプロジェクトは、会議を支援するAIエージェントを提供します。フロントエンドとCloud Runサービスで構成されています。

## ディレクトリ構成
```
.
└── apps/
    ├── frontend/      # フロントエンドアプリケーション
    └── cloudrun/      # Cloud Runサービス
```

## デプロイ方法
このプロジェクトはGitHub Actionsを使用してデプロイされます。  
tagのpushがトリガーになっています。（バックとフロントでトリガーを分けたい ＆ Github Actionsを無料枠に抑えたいので）

### Cloud Runへのデプロイ
先頭が`b`から始まるtagをpushするとデプロイが走ります。
```
b-mmdd-HHMM
```

### Firebase Hostingへのデプロイ
先頭が`f`から始まるtagをpushするとデプロイが走ります。
```
f-mmdd-HHMM
```
