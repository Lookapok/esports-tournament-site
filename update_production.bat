@echo off
REM 生產環境更新腳本
echo 🚀 開始更新生產環境...

REM 激活虛擬環境
call .\venv\Scripts\Activate.bat

REM 檢查是否有未提交的變更
git status --porcelain > nul
if %errorlevel% neq 0 (
    echo ❌ 有未提交的變更，請先提交
    git status
    pause
    exit /b 1
)

REM 本地測試
echo 🧪 執行本地測試...
python manage.py check
if %errorlevel% neq 0 (
    echo ❌ Django 檢查失敗
    pause
    exit /b 1
)

REM 提交並推送
echo 📤 推送到 GitHub...
git push origin master
if %errorlevel% neq 0 (
    echo ❌ Git 推送失敗
    pause
    exit /b 1
)

echo ✅ 更新完成！請等待 3-5 分鐘讓 Render 完成部署
echo 🌐 網站地址: https://winnerstakesall.onrender.com
pause
