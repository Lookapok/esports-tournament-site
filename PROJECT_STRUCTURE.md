# 🏆 WTACS 電競賽事管理系統 - 專案結構說明

## 📁 專案目錄結構

```
esports_project/                    # 🏠 專案根目錄
├── .vscode/                        # VS Code 設定
│   ├── settings.json              # 編輯器設定
│   └── workspace.json             # 工作區設定
│
├── esports_site/                   # 🌐 Django 主應用
├── tournaments/                    # 🏆 錦標賽應用
├── templates/                      # 🎨 模板檔案
├── media/                          # 📷 媒體檔案
├── staticfiles/                    # 📦 靜態檔案
├── fixtures/                       # 💾 測試資料
├── venv/                          # 🐍 Python 虛擬環境
├── logs/                          # 📊 系統日誌
│
├── scripts/                        # 🔧 工具腳本目錄
│   ├── bots/                      # 🤖 Discord 機器人
│   │   ├── bot.py                 # 主要機器人
│   │   ├── bot_minimal.py         # 簡化版本
│   │   ├── bot_simple.py          # 基礎版本
│   │   ├── gemini_test.py         # AI 測試
│   │   └── test_bot.py            # 機器人測試
│   │
│   ├── data/                      # 💾 資料管理
│   │   ├── migrate_*.py           # 資料遷移
│   │   ├── import_*.py            # 資料匯入
│   │   ├── export_*.py            # 資料匯出
│   │   ├── safe_*.py              # 安全操作
│   │   ├── restore_*.py           # 資料還原
│   │   ├── clean_*.py             # 資料清理
│   │   └── compare_*.py           # 資料比對
│   │
│   ├── testing/                   # 🧪 測試檢查
│   │   ├── check_*.py             # 資料檢查
│   │   ├── diagnose_*.py          # 問題診斷
│   │   ├── test_*.py              # 功能測試
│   │   ├── manual_check.py        # 手動檢查
│   │   └── quick_check.py         # 快速檢查
│   │
│   ├── deploy/                    # 🚀 部署相關
│   │   ├── build_fixed.sh         # 修正版建置
│   │   ├── deploy.sh              # 部署腳本
│   │   ├── verify_render_safety.py # 安全驗證
│   │   └── verify_render_safety.sh # 安全檢查
│   │
│   └── monitoring/                # 📊 監控分析
│       ├── cache_manager.py       # 快取管理
│       ├── detailed_performance_analyzer.py # 效能分析
│       ├── django_performance_analyzer.py   # Django 效能
│       └── performance_test.py    # 效能測試
│
├── docs/                          # 📚 專案文檔
│   ├── FINAL_OPTIMIZATION_SUMMARY.md  # 最終優化報告
│   ├── IMMEDIATE_FIXES.md         # 立即修正建議
│   ├── OPTIMIZATION_REPORT.md     # 優化報告
│   ├── SUPABASE_RENDER_SETUP.md   # Supabase 設定
│   └── FOLDER_CLEANUP_PLAN.md     # 清理計劃
│
├── manage.py                      # 🐍 Django 管理入口
├── requirements.txt               # 📋 套件需求
├── build.sh                      # 🔨 建置腳本 (Render)
├── production_data.json          # 💾 生產資料備份
├── render.yaml                   # ⚙️ Render 設定
└── README.md                     # 📖 專案說明
```

## 🎯 使用指南

### 💻 開發環境設定

1. **在 VS Code 中開啟專案**
   ```bash
   cd C:\Users\User\vscode5\esports_project
   code .
   ```

2. **啟用虛擬環境**
   ```bash
   venv\Scripts\activate
   ```

3. **執行開發伺服器**
   ```bash
   python manage.py runserver
   ```

### 🤖 Discord 機器人

- **主要機器人**: `scripts/bots/bot.py`
- **測試機器人**: `scripts/bots/test_bot.py`
- **簡化版本**: `scripts/bots/bot_minimal.py`

### 💾 資料管理

- **Supabase 遷移**: `scripts/data/migrate_to_supabase.py`
- **資料匯入**: `scripts/data/import_production_data.py`
- **安全匯入**: `scripts/data/safe_import.py`
- **資料比對**: `scripts/data/compare_docker_vs_known.py`

### 🧪 測試檢查

- **資料完整性**: `scripts/testing/check_tournaments.py`
- **連線測試**: `scripts/testing/test_supabase_connection.py`
- **問題診斷**: `scripts/testing/diagnose_tournament_9.py`

### 🚀 部署

- **安全檢查**: `scripts/deploy/verify_render_safety.py`
- **Render 部署**: `build.sh`

## 📝 重要注意事項

### ✅ 現在不會再用錯資料夾的原因：

1. **統一工作目錄**: 所有操作都在 `esports_project/` 進行
2. **清晰分類**: 不同類型檔案分別存放在對應目錄
3. **VS Code 設定**: 自動設定正確的工作目錄
4. **腳本路徑**: 所有腳本都有明確的分類位置

### 🔧 工具使用

- **資料檢查**: 使用 `scripts/testing/` 中的檢查工具
- **資料管理**: 使用 `scripts/data/` 中的管理工具
- **部署準備**: 使用 `scripts/deploy/` 中的部署工具
- **效能監控**: 使用 `scripts/monitoring/` 中的監控工具

### 📍 常用命令

```bash
# 切換到專案根目錄
cd C:\Users\User\vscode5\esports_project

# 啟動開發環境
venv\Scripts\activate
python manage.py runserver

# 執行資料檢查
python scripts/testing/check_tournaments.py

# 執行機器人
python scripts/bots/bot.py

# 部署前安全檢查
python scripts/deploy/verify_render_safety.py
```

## 🎉 優化成果

✅ **解決的問題**:
- 雙重目錄結構混亂
- 檔案重複和散落
- 工作目錄不一致
- 腳本分類不明確

✅ **帶來的改善**:
- 清晰的檔案結構
- 邏輯化的分類
- 統一的工作環境
- 更好的維護性
