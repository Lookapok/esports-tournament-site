# 🔧 Supabase + Render 部署設定指南

## 📋 **必要步驟：設定 Supabase DATABASE_URL**

### 1. 🗄️ **取得 Supabase 連接字串**
登入您的 Supabase 控制台：
1. 前往 https://supabase.com/dashboard
2. 選擇您的專案
3. 點擊左側選單的 "Settings" → "Database"
4. 在 "Connection string" 區域，複製 **URI** 格式的連接字串

連接字串格式如下：
```
postgresql://postgres.xxxxxxxxxxxxxxxxxxxx:[YOUR-PASSWORD]@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres
```

### 2. 🌐 **在 Render 中設定環境變數**
1. 登入 Render 控制台：https://dashboard.render.com
2. 找到您的 "wtacs-esports" 服務
3. 點擊服務名稱進入設定頁面
4. 點擊左側的 "Environment"
5. 點擊 "Add Environment Variable"
6. 設定以下變數：

```
Key: DATABASE_URL
Value: [貼上您從 Supabase 複製的完整連接字串]
```

### 3. 🔑 **其他必要環境變數**
同樣在 Render Environment 頁面添加：

```
Key: SECRET_KEY
Value: [生成一個新的 Django Secret Key]

Key: DEBUG
Value: False

Key: ALLOWED_HOSTS
Value: winnertakesall-tw.onrender.com,localhost,127.0.0.1
```

### 4. 🚀 **重新部署**
設定完環境變數後：
1. 在 Render 控制台點擊 "Manual Deploy" → "Deploy latest commit"
2. 或者推送新的代碼變更觸發自動部署

## ⚠️ **重要提醒**

### Supabase 密碼重設
如果您忘記 Supabase 資料庫密碼：
1. 在 Supabase 控制台 → Settings → Database
2. 點擊 "Reset database password"
3. 設定新密碼後更新 DATABASE_URL

### 連接字串格式
確保 DATABASE_URL 包含：
- ✅ 正確的主機名稱
- ✅ 正確的密碼
- ✅ 正確的資料庫名稱 (通常是 `postgres`)
- ✅ 正確的埠號 (通常是 `5432`)

### 測試連接
設定完成後，檢查 Render 部署日誌是否顯示：
```
🗄️ 執行資料庫遷移...
Operations to perform:
  Apply all migrations...
```

如果看到資料庫連接錯誤，請檢查 DATABASE_URL 是否正確。

---
**📞 如需協助，請提供 Render 部署日誌的錯誤訊息！**
