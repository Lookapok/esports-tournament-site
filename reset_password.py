#!/usr/bin/env python
import os
import sys
import django

# 設定 Django 環境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esports_site.settings')
django.setup()

from django.contrib.auth.models import User

def reset_admin_password():
    """重設管理員密碼"""
    
    print("=== 檢查現有管理員帳號 ===")
    
    # 檢查現有的超級管理員
    superusers = User.objects.filter(is_superuser=True)
    
    if superusers.exists():
        print("📋 現有超級管理員帳號：")
        for user in superusers:
            print(f"  👤 用戶名: {user.username}")
            print(f"  📧 Email: {user.email}")
            print(f"  🔐 是否為超級管理員: {user.is_superuser}")
            print(f"  ✅ 是否啟用: {user.is_active}")
            print()
        
        # 重設第一個超級管理員的密碼
        admin_user = superusers.first()
        new_password = "admin123"
        admin_user.set_password(new_password)
        admin_user.save()
        
        print(f"✅ 已重設 '{admin_user.username}' 的密碼")
        print(f"🔑 新密碼: {new_password}")
        print(f"🌐 登入網址: http://127.0.0.1:8000/login/")
        
    else:
        print("❌ 沒有找到超級管理員帳號")
        print("🔧 正在創建新的超級管理員...")
        
        # 創建新的超級管理員
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        
        print("✅ 已創建新的超級管理員")
        print("👤 用戶名: admin")
        print("🔑 密碼: admin123")
        print("📧 Email: admin@example.com")
        print("🌐 登入網址: http://127.0.0.1:8000/login/")

if __name__ == "__main__":
    reset_admin_password()
