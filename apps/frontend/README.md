# ローカル開発環境のセットアップ (React + TypeScript + Vite)

## backendの向き先の変更

API のエンドポイントを変更する場合は、apps/frontend/src/config.ts 内の CLOUD_RUN_ENDPOINT の値を適切に設定してください。

**Cloud Run を使用する場合:**
```ts
const CLOUD_RUN_ENDPOINT = "https://meeting-ai-agent-132459894103.asia-northeast1.run.app";
```
**ローカル環境を使用する場合:**
```ts
const CLOUD_RUN_ENDPOINT = "http://localhost:8080";
```
適切な環境に応じてこの値を変更し、API との通信が正しく行われるようにしてください。

## 依存関係のインストール
```sh
npm install
```

## ローカルサーバーの起動
```sh
npm run dev
```



起動後、ブラウザで `http://localhost:5173/` にアクセスするとアプリケーションが確認できます。
