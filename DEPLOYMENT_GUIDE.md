# 網站部署完整指南

## 🚀 將電競賽事網站發布到網路

### 推薦方案：Render.com 部署

#### 步驟 1：準備專案

**已完成的準備工作：**
- ✅ 所有程式碼已在 GitHub
- ✅ requirements.txt 已準備
- ✅ 環境變數設定完成
- ✅ 部署腳本已建立

#### 步驟 2：註冊 Render.com

1. 前往 https://render.com
2. 使用 GitHub 帳號註冊
3. 連接您的 GitHub 倉庫

#### 步驟 3：建立資料庫

1. 在 Render 控制台點擊「New」→「PostgreSQL」
2. 設定：
   - **Name**: `esports-database`
   - **Region**: 選擇離您最近的區域
   - **PostgreSQL Version**: 16
   - **Plan**: Free（免費方案）
3. 點擊「Create Database」
4. **重要**：複製資料庫連線資訊

#### 步驟 4：建立 Web Service

1. 點擊「New」→「Web Service」
2. 連接 GitHub 倉庫：`esports-tournament-site`
3. 設定：
   - **Name**: `esports-tournament-site`
   - **Region**: 與資料庫相同區域
   - **Branch**: `master`
   - **Root Directory**: `esports_project`
   - **Runtime**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn esports_site.wsgi:application`

#### 步驟 5：設定環境變數

在 Render Web Service 的「Environment」頁面新增：

```
SECRET_KEY=請產生新的密鑰
DEBUG=False
DB_ENGINE=django.db.backends.postgresql
DB_NAME=從步驟3複製的資料庫名稱
DB_USER=從步驟3複製的使用者名稱
DB_PASSWORD=從步驟3複製的密碼
DB_HOST=從步驟3複製的主機位址
DB_PORT=5432
```

#### 步驟 6：部署

1. 點擊「Create Web Service」
2. 等待建置完成（約5-10分鐘）
3. 部署完成後會提供網址，例如：`https://esports-tournament-site.onrender.com`

#### 步驟 7：還原資料（可選）

如果要匯入現有資料：

1. 在 Render 資料庫頁面找到「Connect」
2. 使用提供的 psql 命令連接資料庫
3. 執行：
   ```bash
   psql [資料庫連線字串] < esports_backup.sql
   ```

## 🔧 其他部署選項

### Railway 部署

1. 前往 https://railway.app
2. 使用 GitHub 連接
3. 建立新專案並選擇您的倉庫
4. Railway 會自動偵測 Django 專案
5. 新增 PostgreSQL 資料庫
6. 設定環境變數
7. 部署完成

### Heroku 部署

1. 安裝 Heroku CLI
2. 建立 Heroku app
3. 新增 PostgreSQL addon
4. 設定環境變數
5. 推送程式碼
6. 執行 `heroku run python manage.py migrate`

## ⚙️ 部署前檢查清單

- ✅ `DEBUG=False` 在生產環境
- ✅ 設定正確的 `ALLOWED_HOSTS`
- ✅ 環境變數已設定
- ✅ 靜態檔案收集
- ✅ 資料庫遷移
- ✅ 超級使用者建立

## 🔒 安全設定

### 在生產環境中：

1. **生成新的 SECRET_KEY**：
   ```python
   from django.core.management.utils import get_random_secret_key
   print(get_random_secret_key())
   ```

2. **設定 ALLOWED_HOSTS**：
   ```python
   ALLOWED_HOSTS = ['your-domain.onrender.com', 'your-custom-domain.com']
   ```

3. **確認安全設定**：
   - HTTPS 強制重定向已啟用
   - Cookie 安全設定已設定
   - 安全標頭已配置

## 📊 部署後測試

1. **基本功能測試**：
   - ✅ 網站可以正常訪問
   - ✅ 管理後台可以登入
   - ✅ 資料庫連線正常

2. **功能測試**：
   - ✅ 建立賽事
   - ✅ 新增隊伍
   - ✅ 自動分組
   - ✅ 自動排賽程

3. **效能測試**：
   - ✅ 頁面載入速度
   - ✅ 資料庫查詢效率
   - ✅ 靜態檔案載入

## 🌐 自訂網域（可選）

1. 購買網域名稱
2. 在 Render 中設定 Custom Domain
3. 設定 DNS 記錄
4. SSL 憑證會自動配置

## 📈 監控與維護

1. **Render 提供的監控**：
   - 資源使用情況
   - 錯誤日誌
   - 效能指標

2. **定期備份**：
   - 資料庫定期備份
   - 程式碼版本控制

3. **更新流程**：
   - 推送到 GitHub
   - Render 自動重新部署

## 💰 費用說明

### Render.com 免費方案：
- ✅ Web Service: 750 小時/月（約1個月）
- ✅ PostgreSQL: 90天免費試用
- ⚠️ 閒置時會進入休眠狀態
- ⚠️ 重新啟動需要30秒

### 付費升級（約 $7/月）：
- ✅ 24/7 運行
- ✅ 更快的啟動時間
- ✅ 更多資源

## 🆘 常見問題解決

### 部署失敗問題：

#### 1. psycopg2-binary 版本錯誤
**錯誤信息**：`Could not find a version that satisfies the requirement psycopg2-binary==2.9.11`

**解決方案**：
```bash
# 在 requirements.txt 中使用可用的版本
psycopg2-binary==2.9.10
```

#### 2. build.sh 權限問題
**錯誤信息**：`Permission denied`

**解決方案**：
```bash
# 在 Git 中設定執行權限
git update-index --chmod=+x build.sh
git commit -m "設定 build.sh 執行權限"
git push
```

#### 3. Python 版本問題
**解決方案**：
在 Render 設定中確認 Python Runtime 版本為 `3.11` 或更高

### 資料庫連線錯誤：
1. 檢查環境變數
2. 確認資料庫服務狀態
3. 測試連線字串

### 靜態檔案問題：
1. 確認 `STATIC_ROOT` 設定
2. 執行 `collectstatic`
3. 檢查 WhiteNoise 設定

### 部署流程問題：
1. **檢查建置日誌**：在 Render 控制台查看詳細錯誤信息
2. **確認分支**：確保部署的是正確的 Git 分支
3. **環境變數**：檢查所有必要的環境變數都已設定

現在您的網站就可以在網路上供全世界訪問了！🌍
