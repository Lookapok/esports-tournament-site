# 📁 資料夾結構優化計劃

## 🎯 目標
將混亂的雙層專案結構整理成清晰的單層結構，避免工作目錄混淆。

## 📊 現狀分析

### 問題：
1. **雙重專案結構**：外層 `vscode5/` 和內層 `esports_project/` 都有 Django 檔案
2. **檔案重複**：`manage.py`, `requirements.txt`, `build.sh` 等重複存在
3. **工作目錄混淆**：不確定應該在哪個目錄執行命令
4. **Git 混亂**：兩個 `.git` 目錄可能造成版本控制問題

### 當前重複檔案：
```
外層 (vscode5/)           內層 (esports_project/)
├── manage.py            ├── manage.py ✓ (主要)
├── build.sh             ├── build.sh ✓ (主要)
├── requirements.txt     ├── requirements.txt ✓ (主要)
├── production_data.json ├── production_data.json ✓ (主要)
├── esports_site/        ├── esports_site/ ✓ (主要)
└── tournaments/         ├── tournaments/ ✓ (主要)
```

## 🎯 優化方案

### **方案 1：保留內層，清理外層 (推薦)**
```
c:\Users\User\esports-tournament\   # 重新命名為有意義的名稱
├── esports_site/                   # Django 主應用
├── tournaments/                    # 錦標賽應用
├── manage.py                       # Django 管理
├── requirements.txt                # 套件需求
├── build.sh                        # 部署腳本
├── .env                           # 環境變數
├── README.md                       # 專案說明
└── [清理後的檔案結構]
```

### **方案 2：全新乾淨結構**
```
c:\Users\User\wtacs-tournament\
├── src/                           # 原始碼
│   ├── esports_site/
│   ├── tournaments/
│   └── manage.py
├── scripts/                       # 工具腳本
│   ├── deployment/
│   ├── data_management/
│   └── testing/
├── docs/                          # 文檔
├── config/                        # 設定檔
└── requirements.txt
```

## 🔧 執行步驟

### 第一階段：安全備份
1. 確認 Git 狀態
2. 建立完整備份
3. 確認重要檔案位置

### 第二階段：清理重複檔案
1. 刪除外層重複檔案
2. 保留內層 `esports_project/` 的檔案
3. 移動內層檔案到適當位置

### 第三階段：重新組織
1. 重新命名專案目錄
2. 建立邏輯化的子目錄結構
3. 更新路徑設定

### 第四階段：驗證
1. 測試所有功能
2. 確認部署腳本
3. 更新文檔

## ⚠️ 注意事項
- 備份所有重要資料
- 逐步執行，每步驗證
- 保持 Git 歷史完整
- 更新 Render 部署設定

## 📝 執行檢查清單
- [ ] Git 狀態確認
- [ ] 重要檔案備份
- [ ] 重複檔案識別
- [ ] 清理執行
- [ ] 路徑設定更新
- [ ] 功能測試
- [ ] 部署測試
- [ ] 文檔更新
