## 解決 HTTPS 重定向問題

### 🚀 快速解決方案

#### 方案 1：清除瀏覽器設定
1. **Chrome/Edge:**
   - 按 `F12` 開啟開發者工具
   - 右鍵點擊重新整理按鈕
   - 選擇「清空快取並強制重新整理」
   
2. **或者清除特定網站資料:**
   - Chrome: 設定 → 隱私權和安全性 → 網站設定 → 查看所有網站的權限和資料
   - 搜尋 `127.0.0.1` 或 `localhost`
   - 刪除資料

#### 方案 2：使用無痕模式
- Chrome: `Ctrl + Shift + N`
- Firefox: `Ctrl + Shift + P`
- Edge: `Ctrl + Shift + N`

#### 方案 3：手動輸入完整網址
在網址列輸入：`http://127.0.0.1:8000`
**注意：一定要包含 `http://` 前綴**

#### 方案 4：修改 hosts 檔案（如果需要）
以管理員身份編輯 `C:\Windows\System32\drivers\etc\hosts`
添加：
```
127.0.0.1 localhost
```

#### 方案 5：重置 Chrome HSTS 設定
1. 在 Chrome 網址列輸入：`chrome://net-internals/#hsts`
2. 在 "Delete domain security policies" 區域
3. 輸入 `127.0.0.1` 和 `localhost`
4. 點擊 "Delete"

### ✅ 推薦使用順序
1. 先試無痕模式
2. 再試清除快取
3. 最後考慮重置 HSTS
