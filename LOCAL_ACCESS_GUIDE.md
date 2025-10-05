## 本地 Django 伺服器訪問指南

### ✅ 正確的訪問方式：
- http://127.0.0.1:8000
- http://localhost:8000

### ❌ 錯誤的訪問方式：
- https://127.0.0.1:8000  (不要用 https)
- https://localhost:8000  (不要用 https)

### 🔧 如果還有問題，請嘗試：

1. **清除瀏覽器快取和 Cookie：**
   - Chrome: Ctrl+Shift+Delete
   - Firefox: Ctrl+Shift+Delete
   - Edge: Ctrl+Shift+Delete

2. **使用無痕模式：**
   - Chrome: Ctrl+Shift+N
   - Firefox: Ctrl+Shift+P
   - Edge: Ctrl+Shift+N

3. **手動輸入完整網址：**
   在網址列完整輸入：http://127.0.0.1:8000

### 📊 檢查伺服器狀態：
如果伺服器正常運行，您應該會看到類似這樣的日誌：
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

### 🎯 確認資料恢復狀態：
您的本地資料庫現在有：
- 🏆 1 個賽事 (WTACS S1)
- 👥 31 支隊伍
- 🎮 174 位選手
- 📊 總共 206 筆資料

所有資料都已恢復完成！
