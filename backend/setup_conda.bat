@echo off
REM conda環境のセットアップスクリプト (Windows)

set ENV_NAME=slide-gen-backend
set PYTHON_VERSION=3.11

echo 🚀 Slide Gen Backend - Conda環境セットアップ
echo ==========================================

REM condaがインストールされているか確認
where conda >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ condaがインストールされていません。
    echo    MinicondaまたはAnacondaをインストールしてください:
    echo    https://docs.conda.io/en/latest/miniconda.html
    exit /b 1
)

REM 既存の環境を確認
conda env list | findstr /C:"%ENV_NAME%" >nul
if %ERRORLEVEL% EQU 0 (
    echo ⚠️  環境 '%ENV_NAME%' は既に存在します。
    set /p REPLY="削除して再作成しますか？ (y/N): "
    if /i "%REPLY%"=="y" (
        echo 🗑️  既存の環境を削除中...
        conda env remove -n %ENV_NAME% -y
    ) else (
        echo ✅ 既存の環境を使用します。
        echo    アクティベート: conda activate %ENV_NAME%
        exit /b 0
    )
)

REM 新しいconda環境を作成
echo 📦 Python %PYTHON_VERSION% でconda環境を作成中...
conda create -n %ENV_NAME% python=%PYTHON_VERSION% -y

REM 環境をアクティベート
echo 🔌 環境をアクティベート中...
call conda activate %ENV_NAME%

REM pipをアップグレード
echo ⬆️  pipをアップグレード中...
python -m pip install --upgrade pip

REM 依存関係をインストール
echo 📥 依存関係をインストール中...
pip install -r requirements.txt

REM Playwrightブラウザをインストール
echo 🌐 Playwrightブラウザをインストール中...
playwright install chromium

echo.
echo ✅ セットアップが完了しました！
echo.
echo 次のステップ:
echo 1. 環境をアクティベート: conda activate %ENV_NAME%
echo 2. .envファイルを作成して環境変数を設定
echo 3. サーバーを起動: uvicorn app.main:app --reload --port 3001
echo.

pause

