#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修復排名資料匯入問題
"""

import os
import psycopg2

# 設定 Django 環境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esports_site.settings')

# 手動載入 .env 檔案
try:
    with open('.env', 'r', encoding='utf-8') as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value
except FileNotFoundError:
    print("⚠️ .env 檔案未找到")

import django
django.setup()

from tournaments.models import *
from django.db import transaction

def debug_standings_data():
    """詳細檢查排名資料結構"""
    
    print("🔍 詳細分析排名資料結構")
    print("=" * 50)
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="esports_dev",
            user="postgres",
            password="esports123"
        )
        cursor = conn.cursor()
        
        # 1. 檢查排名表結構
        print("📋 Docker 排名表結構:")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'tournaments_standing' 
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        for i, (col_name, data_type, nullable) in enumerate(columns):
            print(f"  [{i}] {col_name}: {data_type} {'(可空)' if nullable == 'YES' else ''}")
        
        # 2. 檢查實際資料
        print(f"\n📊 Docker 排名資料範例:")
        cursor.execute("SELECT * FROM tournaments_standing ORDER BY id LIMIT 5;")
        samples = cursor.fetchall()
        
        for i, row in enumerate(samples, 1):
            print(f"  範例{i}: {row}")
        
        # 3. 檢查 Supabase Standing 模型欄位
        print(f"\n🏆 Supabase Standing 模型欄位:")
        standing_fields = [field.name for field in Standing._meta.fields]
        for i, field_name in enumerate(standing_fields):
            field = Standing._meta.get_field(field_name)
            print(f"  [{i}] {field_name}: {field.__class__.__name__}")
        
        # 4. 檢查資料對應
        print(f"\n🔗 欄位對應分析:")
        docker_columns = [col[0] for col in columns]
        
        print("Docker 欄位 → Supabase 欄位:")
        for i, docker_col in enumerate(docker_columns):
            if docker_col in standing_fields:
                print(f"  ✅ {docker_col} → {docker_col}")
            else:
                # 嘗試找到對應欄位
                possible_matches = []
                if 'wins' in docker_col or 'won' in docker_col:
                    possible_matches.append('wins')
                elif 'losses' in docker_col or 'lost' in docker_col:
                    possible_matches.append('losses')
                elif 'draw' in docker_col:
                    possible_matches.append('draws')
                elif 'point' in docker_col:
                    possible_matches.append('points')
                elif 'position' in docker_col:
                    possible_matches.append('position')
                
                if possible_matches:
                    print(f"  🔄 {docker_col} → {possible_matches[0]} (推測)")
                else:
                    print(f"  ❌ {docker_col} → ? (無對應)")
        
        cursor.close()
        conn.close()
        return docker_columns, samples
        
    except Exception as e:
        print(f"❌ 檢查失敗: {e}")
        return None, None

def fix_standings_import():
    """修復排名資料匯入"""
    
    print(f"\n🔧 修復排名資料匯入")
    print("=" * 40)
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432", 
            database="esports_dev",
            user="postgres",
            password="esports123"
        )
        cursor = conn.cursor()
        
        # 取得所有排名資料
        cursor.execute("SELECT * FROM tournaments_standing ORDER BY id;")
        standings_data = cursor.fetchall()
        
        # 取得欄位名稱
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'tournaments_standing' 
            ORDER BY ordinal_position;
        """)
        column_names = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        print(f"📊 準備匯入 {len(standings_data)} 筆排名資料")
        print(f"📋 欄位: {column_names}")
        
        imported = 0
        skipped = 0
        errors = 0
        
        with transaction.atomic():
            for row in standings_data:
                try:
                    # 將資料轉換為字典
                    data_dict = dict(zip(column_names, row))
                    
                    # 檢查必要欄位
                    if not data_dict.get('tournament_id') or not data_dict.get('team_id'):
                        print(f"  ⚠️ 跳過無效資料: {data_dict}")
                        skipped += 1
                        continue
                    
                    # 檢查賽事和隊伍是否存在
                    try:
                        tournament = Tournament.objects.get(id=data_dict['tournament_id'])
                        team = Team.objects.get(id=data_dict['team_id'])
                    except (Tournament.DoesNotExist, Team.DoesNotExist) as e:
                        print(f"  ❌ 關聯不存在: {e}")
                        errors += 1
                        continue
                    
                    # 檢查是否已存在
                    existing = Standing.objects.filter(
                        tournament_id=data_dict['tournament_id'],
                        team_id=data_dict['team_id']
                    ).first()
                    
                    if existing:
                        print(f"  ⚠️ 已存在: T{data_dict['tournament_id']}-Team{data_dict['team_id']}")
                        skipped += 1
                        continue
                    
                    # 準備 Standing 資料 (根據實際欄位對應)
                    standing_data = {
                        'id': data_dict.get('id'),
                        'tournament_id': data_dict['tournament_id'],
                        'team_id': data_dict['team_id'],
                        'position': data_dict.get('position', 0),
                        'points': data_dict.get('points', 0),
                        'wins': data_dict.get('wins', 0),  # 直接使用 wins
                        'losses': data_dict.get('losses', 0),  # 直接使用 losses  
                        'draws': data_dict.get('draws', 0),  # 直接使用 draws
                        'matches_played': data_dict.get('wins', 0) + data_dict.get('losses', 0) + data_dict.get('draws', 0)
                    }
                    
                    # 移除 None 值
                    standing_data = {k: v for k, v in standing_data.items() if v is not None}
                    
                    # 建立記錄
                    standing = Standing.objects.create(**standing_data)
                    imported += 1
                    
                    print(f"  ✅ 匯入: T{tournament.id}-Team{team.id} (位置:{standing_data.get('position', 0)})")
                    
                except Exception as e:
                    print(f"  ❌ 匯入失敗: {row[0] if row else 'unknown'} - {e}")
                    errors += 1
        
        print(f"\n📈 匯入結果:")
        print(f"  ✅ 成功: {imported} 筆")
        print(f"  ⚠️ 跳過: {skipped} 筆") 
        print(f"  ❌ 失敗: {errors} 筆")
        
        return imported
        
    except Exception as e:
        print(f"❌ 修復失敗: {e}")
        import traceback
        traceback.print_exc()
        return 0

def verify_standings():
    """驗證排名資料"""
    
    print(f"\n🔍 驗證排名資料")
    print("=" * 30)
    
    standings_count = Standing.objects.count()
    print(f"📊 總排名記錄: {standings_count}")
    
    if standings_count > 0:
        print(f"\n📋 各小組排名:")
        for group in Group.objects.all():
            group_standings = Standing.objects.filter(tournament=group.tournament).count()
            print(f"  🏆 {group.name}: 相關排名 {group_standings} 筆")
        
        # 顯示一些範例
        print(f"\n🏅 前5名排名:")
        top_standings = Standing.objects.order_by('position')[:5]
        for standing in top_standings:
            team_name = standing.team.name if standing.team else "未知隊伍"
            print(f"  {standing.position}. {team_name} - {standing.points}分 ({standing.wins}勝{standing.losses}敗)")

def main():
    """主函數"""
    
    print("🔧 修復排名資料匯入問題")
    print("=" * 60)
    
    try:
        # 1. 分析資料結構
        columns, samples = debug_standings_data()
        if not columns:
            return
        
        # 2. 修復匯入
        imported_count = fix_standings_import()
        
        # 3. 驗證結果
        verify_standings()
        
        print(f"\n" + "=" * 60)
        if imported_count > 0:
            print("🎉 排名資料修復完成！")
            print(f"📊 成功匯入 {imported_count} 筆排名資料")
        else:
            print("⚠️ 沒有新的排名資料匯入")
        
    except Exception as e:
        print(f"❌ 修復過程發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
