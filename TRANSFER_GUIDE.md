# 專案轉移指南

## 📋 轉移到新電腦的完整步驟

### 1. 在新電腦上安裝必要軟體

#### 必須安裝：
- **Python 3.13+** - https://www.python.org/downloads/
- **PostgreSQL 16** - https://www.postgresql.org/download/
- **Git** - https://git-scm.com/downloads
- **VS Code** - https://code.visualstudio.com/

#### PostgreSQL 設定：
```sql
-- 以 postgres 使用者身分執行
CREATE DATABASE esports_dev;
CREATE USER postgres WITH PASSWORD 'your-password';
GRANT ALL PRIVILEGES ON DATABASE esports_dev TO postgres;
```

### 2. 複製專案程式碼

```bash
# 從 GitHub 複製專案
git clone https://github.com/Lookapok/esports-tournament-site.git
cd esports-tournament-site

# 切換到專案目錄
cd esports_project
```

### 3. 建立虛擬環境

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. 安裝相依套件

```bash
pip install -r requirements.txt
```

### 5. 環境變數設定

```bash
# 複製環境變數範例檔案
copy .env.example .env

# 編輯 .env 檔案，設定：
# - SECRET_KEY（產生新的密鑰）
# - DEBUG=True（開發環境）
# - 資料庫連線資訊
```

#### 產生新的 SECRET_KEY：
```python
# 在 Python 中執行
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### 6. 資料庫遷移

```bash
# 建立遷移檔案
python manage.py makemigrations

# 執行遷移
python manage.py migrate

# 建立超級使用者
python manage.py createsuperuser
```

### 7. 收集靜態檔案

```bash
python manage.py collectstatic
```

### 8. 啟動開發伺服器

```bash
python manage.py runserver
```

### 9. 驗證功能

訪問 http://127.0.0.1:8000 確認：
- ✅ 網站正常運行
- ✅ 可以登入管理後台
- ✅ 可以建立賽事
- ✅ 自動分組功能正常
- ✅ 自動排賽程功能正常

## 🔧 常見問題解決

### 問題 1：PostgreSQL 連線失敗
- 確認 PostgreSQL 服務已啟動
- 檢查 .env 檔案中的資料庫設定
- 確認資料庫和使用者已建立

### 問題 2：靜態檔案無法載入
```bash
python manage.py collectstatic --clear
```

### 問題 3：缺少套件
```bash
pip install -r requirements.txt --force-reinstall
```

## 📁 重要檔案說明

- `.env` - 環境變數（不要提交到 Git）
- `requirements.txt` - Python 套件清單
- `db.sqlite3` - SQLite 資料庫檔案（如果使用）
- `media/` - 使用者上傳檔案
- `staticfiles/` - 靜態檔案收集目錄

## 🔒 安全注意事項

1. **不要**將 `.env` 檔案提交到 Git
2. 在生產環境設定 `DEBUG=False`
3. 使用強密碼和新的 SECRET_KEY
4. 定期備份資料庫

## 🚀 部署到生產環境

如需部署到 Render.com 或其他平台，請：
1. 設定環境變數
2. 確認 `requirements.txt` 完整
3. 檢查 `ALLOWED_HOSTS` 設定
4. 啟用所有安全設定
