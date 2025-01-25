## ローカル実行手順

### Google Cloud認証情報の取得

下記リンクを参考にユーザー認証情報を取得する  
https://cloud.google.com/docs/authentication/set-up-adc-local-dev-environment?hl=ja

### Dockerを使わず起動

```bash
cd apps/cloudrun
.\venv\Scripts\activate
pip install -r requirements.txt
python .\main.py
```

### Dockerで起動
1. **Dockerのインストール**: Dockerがインストールされていることを確認してください。インストールされていない場合は、[Dockerの公式サイト](https://www.docker.com/get-started)からインストールしてください。

2. **Dockerイメージのビルド**: `apps/cloudrun`ディレクトリに移動し、Dockerイメージをビルドします。

   ```bash
   cd apps/cloudrun
   docker build -t cloudrun-app .
   ```

3. **Dockerコンテナの実行**: ビルドが成功したら、以下のコマンドでコンテナを実行します。

   ```bash
   docker run -p 8080:8080 cloudrun-app
   ```

このコマンドは、コンテナの8080ポートをホストの8080ポートにマッピングします。これにより、ブラウザで`http://localhost:8080`にアクセスすることでアプリケーションを確認できます。
