"""
部署前檢查腳本
確保所有設定都正確配置用於生產環境
"""

import os
from django.core.management.utils import get_random_secret_key

def check_deployment_readiness():
    print("🔍 檢查部署準備狀況...")
    
    # 檢查環境變數
    required_vars = [
        'SECRET_KEY',
        'DB_ENGINE', 
        'DB_NAME',
        'DB_USER', 
        'DB_PASSWORD',
        'DB_HOST'
    ]
    
    print("\n📋 環境變數檢查:")
    for var in required_vars:
        if var in os.environ:
            print(f"✅ {var}: 已設定")
        else:
            print(f"❌ {var}: 未設定")
    
    # 檢查 DEBUG 設定
    debug = os.environ.get('DEBUG', 'True').lower()
    if debug == 'false':
        print("✅ DEBUG: False (生產環境)")
    else:
        print("⚠️  DEBUG: True (開發環境)")
    
    print(f"\n🔑 如需新的 SECRET_KEY:")
    print(f"SECRET_KEY={get_random_secret_key()}")
    
    print(f"\n🌐 部署後請測試:")
    print(f"1. 網站基本功能")
    print(f"2. 管理後台登入")
    print(f"3. 賽事建立功能")
    print(f"4. 自動分組功能")

if __name__ == "__main__":
    check_deployment_readiness()
