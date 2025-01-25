FROM mcr.microsoft.com/devcontainers/python:3.11

# 必要なパッケージのインストール
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリの設定
WORKDIR /workspace 