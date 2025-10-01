@echo off
echo ================================
echo PostgreSQL 升級腳本
echo ================================

echo.
echo 步驟 1: 檢查 Docker 狀態
docker --version
if %errorlevel% neq 0 (
    echo ERROR: Docker 未安裝或未啟動
    echo 請先啟動 Docker Desktop 後再執行此腳本
    pause
    exit /b 1
)

echo.
echo 步驟 2: 建立 PostgreSQL 容器
docker run --name postgres-esports -e POSTGRES_DB=esports_db -e POSTGRES_USER=esports_user -e POSTGRES_PASSWORD=esports_password123 -p 5432:5432 --restart=unless-stopped -d postgres:16

if %errorlevel% neq 0 (
    echo 容器可能已存在，嘗試啟動現有容器...
    docker start postgres-esports
)

echo.
echo 步驟 3: 等待資料庫啟動
timeout /t 10 /nobreak

echo.
echo 步驟 4: 執行資料庫遷移
python manage.py makemigrations
python manage.py migrate

echo.
echo 步驟 5: 匯出 SQLite 資料
python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission > data_backup.json

echo.
echo 步驟 6: 載入資料到 PostgreSQL
python manage.py loaddata data_backup.json

echo.
echo 步驟 7: 建立超級使用者（如果需要）
python manage.py createsuperuser

echo.
echo ================================
echo 升級完成！
echo ================================
echo.
echo 以後重開伺服器只需要執行：
echo python manage.py runserver
echo.
echo PostgreSQL 容器設定為自動啟動，
echo 所以重開電腦後不需要手動啟動資料庫。
echo.
pause
