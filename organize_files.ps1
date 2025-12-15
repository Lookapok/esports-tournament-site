# 📁 檔案整理腳本

Write-Host "🔧 開始整理專案檔案結構..." -ForegroundColor Green

# 確保在正確的目錄
$projectRoot = "C:\Users\User\vscode5\esports_project"
Set-Location $projectRoot

Write-Host "📍 當前工作目錄: $(Get-Location)" -ForegroundColor Yellow

# 移動機器人相關檔案到 scripts/bots/
Write-Host "🤖 移動機器人檔案..." -ForegroundColor Cyan
$botFiles = @("bot.py", "bot_minimal.py", "bot_simple.py", "gemini_test.py", "test_bot.py")
foreach ($file in $botFiles) {
    if (Test-Path $file) {
        Move-Item $file "scripts\bots\" -Force
        Write-Host "✅ 移動 $file 到 scripts\bots\" -ForegroundColor Green
    }
}

# 移動外層的機器人檔案
$outerBotFiles = @("..\bot.py", "..\bot_minimal.py", "..\bot_simple.py", "..\gemini_test.py", "..\test_bot.py")
foreach ($file in $outerBotFiles) {
    if (Test-Path $file) {
        $fileName = Split-Path $file -Leaf
        Copy-Item $file "scripts\bots\" -Force
        Write-Host "📋 複製外層 $fileName 到 scripts\bots\" -ForegroundColor Blue
    }
}

# 移動測試腳本到 scripts/testing/
Write-Host "🧪 移動測試檔案..." -ForegroundColor Cyan
$testFiles = @(
    "check_*.py", 
    "diagnose_*.py", 
    "test_*.py", 
    "manual_check.py", 
    "quick_check.py"
)
Get-ChildItem -Name -Include $testFiles | ForEach-Object {
    if ($_ -notlike "*bot*") {  # 排除已移動的 bot 檔案
        Move-Item $_ "scripts\testing\" -Force
        Write-Host "✅ 移動 $_ 到 scripts\testing\" -ForegroundColor Green
    }
}

# 移動資料管理腳本到 scripts/data/
Write-Host "💾 移動資料管理檔案..." -ForegroundColor Cyan
$dataFiles = @(
    "migrate_*.py", 
    "import_*.py", 
    "export_*.py", 
    "safe_*.py", 
    "restore_*.py", 
    "clean_*.py", 
    "compare_*.py",
    "emergency_restore.py",
    "data_cleanup_validator.py",
    "run_force_reimport.py",
    "trigger_import.py"
)
Get-ChildItem -Name -Include $dataFiles | ForEach-Object {
    Move-Item $_ "scripts\data\" -Force
    Write-Host "✅ 移動 $_ 到 scripts\data\" -ForegroundColor Green
}

# 移動部署腳本到 scripts/deploy/
Write-Host "🚀 移動部署檔案..." -ForegroundColor Cyan
$deployFiles = @("deploy.sh", "build_fixed.sh", "verify_render_safety.py", "verify_render_safety.sh")
foreach ($file in $deployFiles) {
    if (Test-Path $file) {
        Move-Item $file "scripts\deploy\" -Force
        Write-Host "✅ 移動 $file 到 scripts\deploy\" -ForegroundColor Green
    }
}

# 移動監控腳本到 scripts/monitoring/
Write-Host "📊 移動監控檔案..." -ForegroundColor Cyan
$monitorFiles = @("*performance*.py", "cache_manager.py")
Get-ChildItem -Name -Include $monitorFiles | ForEach-Object {
    Move-Item $_ "scripts\monitoring\" -Force
    Write-Host "✅ 移動 $_ 到 scripts\monitoring\" -ForegroundColor Green
}

# 移動文檔到 docs/
Write-Host "📚 移動文檔檔案..." -ForegroundColor Cyan
$docFiles = @("*.md", "README_new.md")
Get-ChildItem -Name -Include $docFiles | ForEach-Object {
    if ($_ -ne "README.md") {  # 保留主要 README
        Move-Item $_ "docs\" -Force
        Write-Host "✅ 移動 $_ 到 docs\" -ForegroundColor Green
    }
}

# 移動外層文檔
$outerDocFiles = @("..\*.md")
Get-ChildItem $outerDocFiles | ForEach-Object {
    if ($_.Name -ne "README.md") {
        Copy-Item $_.FullName "docs\" -Force
        Write-Host "📋 複製外層 $($_.Name) 到 docs\" -ForegroundColor Blue
    }
}

Write-Host "`n🎉 檔案整理完成！" -ForegroundColor Green
Write-Host "📁 新的目錄結構：" -ForegroundColor Yellow
Write-Host "  scripts/bots/     - Discord 機器人檔案"
Write-Host "  scripts/data/     - 資料管理腳本"
Write-Host "  scripts/deploy/   - 部署相關腳本"
Write-Host "  scripts/testing/  - 測試檢查腳本"
Write-Host "  scripts/monitoring/ - 效能監控腳本"
Write-Host "  docs/            - 專案文檔"

Write-Host "`n📝 接下來建議：" -ForegroundColor Cyan
Write-Host "1. 在 VS Code 中重新開啟 esports_project 目錄"
Write-Host "2. 檢查移動後的檔案是否正常運作"
Write-Host "3. 更新相關的匯入路徑"
