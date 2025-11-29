# 🚀 Supabase 設定完整指南

## 📝 設定檢查清單

### ✅ 第一階段：建立帳戶和專案

1. **前往 Supabase**
   - 網址：https://supabase.com
   - 點擊右上角「Sign in」或「Start your project」

2. **註冊/登入**
   - 推薦使用 GitHub 帳戶（一鍵登入）
   - 或使用 Google 帳戶

3. **建立新專案**
   ```
   ✅ Organization: 選擇您的帳戶
   ✅ Project name: wtacs-esports
   ✅ Database Password: 設定強密碼並記住
   ✅ Region: Southeast Asia (Singapore)
   ✅ Pricing Plan: Free
   ```

4. **等待專案建立**
   - ⏰ 通常需要 2-3 分鐘
   - 🔄 會顯示建立進度
   - ✅ 完成後會進入專案儀表板

### ✅ 第二階段：取得連線資訊

1. **進入資料庫設定**
   ```
   左側選單 → Settings (齒輪圖示) → Database
   ```

2. **找到連線字串**
   ```
   向下滾動到「Connection string」區段
   選擇「URI」標籤（不是 Session mode）
   點擊「Copy」按鈕複製完整字串
   ```

3. **連線字串格式範例**
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
   ```
   
   其中：
   - `[YOUR-PASSWORD]`：您設定的資料庫密碼
   - `[PROJECT-REF]`：專案的唯一識別碼（20個字母）

### ✅ 第三階段：驗證設定

**重要提醒：**
- 🕐 專案建立後需要等待 5-10 分鐘才能完全可用
- 🌐 確保網路連線正常
- 🔑 密碼中不能包含特殊字元如 @ # $ 等

**如果遇到連線問題：**
1. 檢查專案是否顯示「Building」或「Ready」
2. 等待幾分鐘後再次嘗試
3. 確認密碼輸入正確
4. 檢查防火牆設定

## 🎯 下一步：部署到 Render

當 Supabase 設定完成後，我們將：

1. ✅ 更新環境變數設定
2. ✅ 設定 Render Web Service
3. ✅ 執行資料庫遷移
4. ✅ 測試線上系統

## 📞 需要協助？

如果在任何步驟遇到問題，請截圖並提供：
- 錯誤訊息
- 您的 Supabase 專案狀態
- 連線字串（隱藏密碼部分）

我會立即協助您解決！
