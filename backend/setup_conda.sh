#!/bin/bash

# conda環境のセットアップスクリプト

ENV_NAME="slide-gen-backend"
PYTHON_VERSION="3.11"

echo "🚀 Slide Gen Backend - Conda環境セットアップ"
echo "=========================================="

# condaがインストールされているか確認
if ! command -v conda &> /dev/null; then
    echo "❌ condaがインストールされていません。"
    echo "   MinicondaまたはAnacondaをインストールしてください:"
    echo "   https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

# 既存の環境を確認
if conda env list | grep -q "^${ENV_NAME} "; then
    echo "⚠️  環境 '${ENV_NAME}' は既に存在します。"
    read -p "削除して再作成しますか？ (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  既存の環境を削除中..."
        conda env remove -n ${ENV_NAME} -y
    else
        echo "✅ 既存の環境を使用します。"
        echo "   アクティベート: conda activate ${ENV_NAME}"
        exit 0
    fi
fi

# 新しいconda環境を作成
echo "📦 Python ${PYTHON_VERSION} でconda環境を作成中..."
conda create -n ${ENV_NAME} python=${PYTHON_VERSION} -y

# 環境をアクティベート
echo "🔌 環境をアクティベート中..."
eval "$(conda shell.bash hook)"
conda activate ${ENV_NAME}

# pipをアップグレード
echo "⬆️  pipをアップグレード中..."
pip install --upgrade pip

# 依存関係をインストール
echo "📥 依存関係をインストール中..."
pip install -r requirements.txt

# Playwrightブラウザをインストール
echo "🌐 Playwrightブラウザをインストール中..."
playwright install chromium

echo ""
echo "✅ セットアップが完了しました！"
echo ""
echo "次のステップ:"
echo "1. 環境をアクティベート: conda activate ${ENV_NAME}"
echo "2. .envファイルを作成して環境変数を設定"
echo "3. サーバーを起動: uvicorn app.main:app --reload --port 3001"
echo ""

