# 🔧 立即資料夾優化執行計劃

## ✅ 確認狀態

**好消息：** 目前你的主要工作目錄是 `esports_project/`，這是正確的！

**當前工作目錄：** `C:\Users\User\vscode5\esports_project\`
**主要 Django 專案：** ✓ 位於正確位置
**重要檔案：** ✓ manage.py, build.sh, requirements.txt 都在此目錄

## 🎯 立即優化建議

### 1. **修正 VS Code 工作區設定**

建議在 VS Code 中：
1. 關閉目前工作區
2. 重新開啟 `esports_project` 作為根目錄
3. 這樣可以避免路徑混淆

### 2. **建立 .vscode/settings.json 設定**

在 `esports_project/` 目錄建立 `.vscode/settings.json`：

```json
{
    "python.defaultInterpreterPath": "./venv/Scripts/python.exe",
    "terminal.integrated.cwd": "${workspaceFolder}",
    "files.exclude": {
        "**/__pycache__": true,
        "**/venv": false,
        "**/.git": false,
        "**/node_modules": true
    },
    "python.terminal.activateEnvironment": true
}
```

### 3. **清理外層重複檔案 (可選)**

外層 `vscode5/` 目錄的重複檔案可以安全移除：
- `manage.py` (保留 esports_project/ 內的)
- `bot*.py` (移動到 scripts/ 目錄)
- 重複的 requirements.txt
- 重複的 build.sh

### 4. **建立清晰的腳本目錄結構**

```
esports_project/
├── scripts/
│   ├── bots/           # Discord 機器人
│   ├── data/           # 資料管理腳本
│   ├── deploy/         # 部署腳本  
│   └── testing/        # 測試腳本
├── docs/               # 文檔
├── config/             # 設定檔
└── [Django 核心檔案]
```

## 📝 執行檢查清單

- [x] 確認主要工作目錄在 `esports_project/`
- [ ] 設定 VS Code 工作區為 `esports_project/`
- [ ] 建立 `.vscode/settings.json`
- [ ] 整理腳本到 `scripts/` 目錄
- [ ] 清理外層重複檔案
- [ ] 更新 README 說明

## ⚡ 快速修正命令

```bash
# 1. 設定工作目錄為 esports_project
cd C:\Users\User\vscode5\esports_project

# 2. 建立腳本目錄
mkdir scripts scripts\bots scripts\data scripts\deploy scripts\testing

# 3. 移動檔案到適當位置
move ..\bot*.py scripts\bots\
move check_*.py scripts\testing\
move diagnose_*.py scripts\testing\
move migrate_*.py scripts\data\

# 4. 建立 .vscode 目錄和設定
mkdir .vscode
```

## 🔍 為什麼會用錯資料夾的根本原因

1. **VS Code 開啟了外層目錄** `vscode5/` 而不是 `esports_project/`
2. **終端機有時在外層，有時在內層**
3. **重複檔案造成混淆** - 不確定該編輯哪一個
4. **沒有統一的工作目錄規範**

## 💡 長期解決方案

建議將 `esports_project/` 重新命名為有意義的名稱，並直接作為專案根目錄：

```
C:\Users\User\wtacs-tournament\
├── esports_site/       # Django 主應用
├── tournaments/        # 錦標賽應用  
├── scripts/           # 所有工具腳本
├── docs/              # 文檔
├── config/            # 設定檔
├── manage.py          # Django 管理
└── requirements.txt    # 套件需求
```

這樣可以完全避免雙層目錄的混淆問題。
