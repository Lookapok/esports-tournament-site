# 🏆 WTACS 電競賽事管理系統

一個基於 Django 的現代化電競錦標賽管理平台，支援即時積分排行榜、比賽管理和 Discord 機器人整合。

## ✨ 主要功能

- 🎮 **錦標賽管理** - 支援單淘汰、雙淘汰等多種賽制
- 👥 **隊伍管理** - 隊伍資訊、選手管理、頭像上傳
- ⚔️ **比賽記錄** - 詳細的比賽資料和戰績統計
- 📊 **即時排行榜** - 自動計算積分和排名
- 🤖 **Discord 整合** - REST API 支援 Discord 機器人
- 📱 **響應式設計** - 支援桌面和行動裝置
- 🔐 **管理員後台** - 完整的資料管理介面

## 🚀 快速開始

### 本地開發

1. **克隆專案**
   ```bash
   git clone https://github.com/Lookapok/esports-tournament-site.git
   cd esports-tournament-site/esports_project
   ```

2. **建立虛擬環境**
   ```bash
   python -m venv venv
   venv\Scripts\activate     # Windows
   ```

3. **安裝依賴**
   ```bash
   pip install -r requirements.txt
   ```

4. **設定環境變數**
   ```bash
   copy .env.example .env
   # 編輯 .env 檔案，設定資料庫連線等
   ```

5. **執行遷移**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **啟動開發伺服器**
   ```bash
   python manage.py runserver
   ```

## 🔧 技術架構

### 核心技術
- **後端**: Django 5.2.5 + Django REST Framework
- **資料庫**: PostgreSQL (生產) / SQLite (開發)
- **快取**: Redis (生產) / 內存快取 (開發)
- **靜態檔案**: WhiteNoise
- **部署**: Render + Supabase

### 主要套件
```
Django==5.2.5
djangorestframework==3.16.1
django-tables2==2.7.5
psycopg2-binary>=2.8.6
gunicorn==23.0.0
Pillow>=9.0.0
discord.py==2.5.2
```

## 📁 專案結構

```
esports_project/
├── esports_site/          # Django 主要設定
├── tournaments/           # 錦標賽應用程式
├── monitoring/           # 監控中介軟體
├── templates/            # HTML 模板
├── media/               # 使用者上傳檔案
├── staticfiles/         # 靜態檔案
├── manage.py           # Django 管理腳本
├── requirements.txt    # Python 依賴
└── build.sh           # 部署腳本
```

## 🌐 線上展示

- **網站**: https://winnertakesall-tw.onrender.com
- **管理員**: https://winnertakesall-tw.onrender.com/admin/
  - 帳號: `admin` / 密碼: `wtacs2024`
- **API**: https://winnertakesall-tw.onrender.com/api/

## 📊 API 文檔

### 錦標賽 API
- `GET /api/tournaments/` - 取得所有錦標賽
- `GET /api/tournaments/{id}/standings/` - 取得積分榜

### 隊伍 API
- `GET /api/teams/` - 取得所有隊伍
- `GET /api/teams/{id}/` - 取得特定隊伍資訊

### Discord 機器人 API
- `GET /api/search/teams/?q={query}` - 搜尋隊伍
- `GET /api/search/players/?q={query}` - 搜尋選手

## 🔑 環境變數

| 變數名 | 說明 | 預設值 |
|--------|------|--------|
| `SECRET_KEY` | Django 密鑰 | - |
| `DEBUG` | 除錯模式 | `False` |
| `DATABASE_URL` | 資料庫連線 | SQLite |
| `RENDER` | Render 環境 | `False` |

## 📄 授權

本專案採用 MIT 授權條款。

---

**WTACS 電競賽事管理系統** - 為電競賽事而生 🎮
