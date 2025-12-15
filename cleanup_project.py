#!/usr/bin/env python
"""
代碼清理和優化腳本
清除不必要的檔案，保留核心功能
"""

import os
import shutil
from pathlib import Path

def cleanup_project():
    """清理專案不必要的檔案"""
    
    # 要刪除的檔案列表
    files_to_remove = [
        # 測試檔案
        'test_views.py',
        'test_logging.py',
        'test_deployment.py',
        'test_opponent_display.py',
        'test_url.py',
        
        # 備份和還原檔案
        'backup_data.py',
        'check_backup.py',
        'check_backup_data.py',
        'check_groups_teams.py',
        'check_kinyi_data.py',
        'check_local_data.py',
        'restore_complete_data.py',
        'restore_kinyi_team.py',
        'restore_team_code.py',
        'restore_team_code_enhanced.py',
        'safe_restore_team.py',
        'reset_password.py',
        
        # 性能分析檔案
        'performance_test.py',
        'django_performance_analyzer.py',
        'detailed_performance_analyzer.py',
        'data_cleanup_validator.py',
        'cache_manager.py',
        
        # 舊的設定檔案
        '.env.local',
        '.env.local.backup',
        '.env.render',
        '.env.supabase',
        'password_reset_commands.txt',
        
        # 舊的部署檔案
        'deploy.sh',
        'docker-compose.yml',
        'Dockerfile',
        'update_production.bat',
        'upgrade_to_postgresql.bat',
        'upgrade_to_postgresql.sh',
        
        # JSON 資料檔案
        'backup_utf8.json',
        'local_backup_fixed_20251005_205426.json',
        'cache_diagnostic_report.json',
        'detailed_performance_analysis.json',
        'performance_test_results.json',
        'production_tournament_data.json',
        
        # SQL 備份檔案
        'esports_backup.sql',
        
        # 舊的匯出入檔案
        'export_data.py',
        'export_production_data.py',
        'import_production_data.py',
        'generate_utf8_fixtures.py',
        
        # 文件檔案（保留核心文件）
        'ELIMINATION_ALGORITHMS.md',
        'HTTPS_FIX_GUIDE.md',
        'LOCAL_ACCESS_GUIDE.md',
        'MONITORING_REPORT.md',
        'SUPABASE_SETUP_GUIDE.md',
        'SYSTEM_MANUAL.md',
    ]
    
    # 要保留的核心檔案
    core_files = [
        'manage.py',
        'requirements.txt',
        'requirements.production.txt',
        'build.sh',
        'render.yaml',
        '.gitignore',
        'README.md',
        '.env.example',
        '.env.production',
        'production_data.json',  # 保留主要資料檔案
    ]
    
    base_dir = Path('.')
    removed_count = 0
    
    print("🧹 開始清理專案檔案...")
    
    for file_name in files_to_remove:
        file_path = base_dir / file_name
        if file_path.exists():
            try:
                file_path.unlink()
                print(f"  ✅ 已刪除: {file_name}")
                removed_count += 1
            except Exception as e:
                print(f"  ❌ 刪除失敗: {file_name} - {e}")
    
    # 清理空的 logs 目錄內容（保留目錄結構）
    logs_dir = base_dir / 'logs'
    if logs_dir.exists():
        for log_file in logs_dir.glob('*.log'):
            log_file.unlink()
            print(f"  ✅ 已清理日誌: {log_file.name}")
    
    print(f"\n🎉 清理完成！共刪除 {removed_count} 個檔案")
    print("\n📋 保留的核心檔案:")
    for core_file in core_files:
        if (base_dir / core_file).exists():
            print(f"  📄 {core_file}")
    
    print("\n📁 保留的核心目錄:")
    core_dirs = ['esports_site', 'tournaments', 'monitoring', 'templates', 'media', 'staticfiles']
    for core_dir in core_dirs:
        if (base_dir / core_dir).exists():
            print(f"  📁 {core_dir}/")

if __name__ == "__main__":
    cleanup_project()
