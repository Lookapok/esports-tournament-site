#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
補齊剩餘的關聯資料：小組-隊伍關聯、排名資料、賽事-參賽者關聯
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

def get_docker_missing_data():
    """從 Docker 取得缺少的關聯資料"""
    
    print("🐳 從 Docker 取得關聯資料")
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
        
        data = {}
        
        # 1. 小組-隊伍關聯
        print("📋 取得小組-隊伍關聯...")
        cursor.execute("SELECT group_id, team_id FROM tournaments_group_teams ORDER BY group_id, team_id;")
        data['group_teams'] = cursor.fetchall()
        print(f"  📊 找到 {len(data['group_teams'])} 筆關聯")
        
        # 2. 排名資料
        print("📊 取得排名資料...")
        cursor.execute("SELECT * FROM tournaments_standing ORDER BY id;")
        data['standings'] = cursor.fetchall()
        print(f"  📊 找到 {len(data['standings'])} 筆排名")
        
        # 檢查排名表結構
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'tournaments_standing' 
            ORDER BY ordinal_position;
        """)
        data['standing_columns'] = [row[0] for row in cursor.fetchall()]
        print(f"  📋 排名表欄位: {data['standing_columns']}")
        
        # 3. 賽事-參賽者關聯
        print("🏆 取得賽事-參賽者關聯...")
        cursor.execute("SELECT tournament_id, team_id FROM tournaments_tournament_participants ORDER BY tournament_id, team_id;")
        data['tournament_participants'] = cursor.fetchall()
        print(f"  📊 找到 {len(data['tournament_participants'])} 筆參賽者")
        
        # 顯示一些範例資料
        if data['group_teams']:
            print(f"\n🔍 小組-隊伍關聯範例:")
            for i, (group_id, team_id) in enumerate(data['group_teams'][:3], 1):
                print(f"  {i}. 小組 {group_id} ← 隊伍 {team_id}")
        
        if data['standings']:
            print(f"\n🔍 排名資料範例:")
            for i, row in enumerate(data['standings'][:3], 1):
                print(f"  {i}. {row[:5]}...")
        
        cursor.close()
        conn.close()
        return data
        
    except Exception as e:
        print(f"❌ Docker 連接失敗: {e}")
        return None

def import_group_teams(group_teams_data):
    """匯入小組-隊伍關聯"""
    
    print("\n🔗 匯入小組-隊伍關聯")
    print("=" * 40)
    
    imported = 0
    errors = 0
    
    with transaction.atomic():
        for group_id, team_id in group_teams_data:
            try:
                # 確認小組和隊伍都存在
                group = Group.objects.get(id=group_id)
                team = Team.objects.get(id=team_id)
                
                # 添加關聯（如果不存在）
                if not group.teams.filter(id=team_id).exists():
                    group.teams.add(team)
                    imported += 1
                    
            except Group.DoesNotExist:
                print(f"  ❌ 小組 {group_id} 不存在")
                errors += 1
            except Team.DoesNotExist:
                print(f"  ❌ 隊伍 {team_id} 不存在")
                errors += 1
            except Exception as e:
                print(f"  ❌ 關聯 {group_id}-{team_id} 失敗: {e}")
                errors += 1
    
    print(f"✅ 匯入完成: {imported} 筆成功, {errors} 筆失敗")
    return imported

def import_standings(standings_data, columns):
    """匯入排名資料"""
    
    print("\n📊 匯入排名資料")
    print("=" * 40)
    
    imported = 0
    errors = 0
    skipped = 0
    
    with transaction.atomic():
        for row in standings_data:
            try:
                # 解析欄位（根據實際欄位結構）
                data_dict = dict(zip(columns, row))
                
                # 檢查必要欄位
                if not data_dict.get('tournament_id') or not data_dict.get('team_id'):
                    print(f"  ⚠️ 跳過無效資料: {row[:3]}...")
                    skipped += 1
                    continue
                
                # 確認賽事和隊伍存在
                try:
                    tournament = Tournament.objects.get(id=data_dict['tournament_id'])
                    team = Team.objects.get(id=data_dict['team_id'])
                except (Tournament.DoesNotExist, Team.DoesNotExist):
                    print(f"  ❌ 賽事或隊伍不存在: T{data_dict['tournament_id']}, Team{data_dict['team_id']}")
                    errors += 1
                    continue
                
                # 檢查是否已存在
                if Standing.objects.filter(
                    tournament_id=data_dict['tournament_id'], 
                    team_id=data_dict['team_id']
                ).exists():
                    skipped += 1
                    continue
                
                # 創建排名記錄
                standing_data = {
                    'id': data_dict.get('id'),
                    'tournament_id': data_dict['tournament_id'],
                    'team_id': data_dict['team_id'],
                    'position': data_dict.get('position', 0),
                    'points': data_dict.get('points', 0),
                    'wins': data_dict.get('matches_won', 0),
                    'losses': data_dict.get('matches_lost', 0),
                    'draws': data_dict.get('draws', 0),
                    'matches_played': data_dict.get('matches_played', 0)
                }
                
                # 移除 None 值
                standing_data = {k: v for k, v in standing_data.items() if v is not None}
                
                Standing.objects.create(**standing_data)
                imported += 1
                
                if imported % 10 == 0:
                    print(f"  📊 已匯入 {imported} 筆排名...")
                
            except Exception as e:
                print(f"  ❌ 排名資料 {row[0] if row else 'unknown'} 匯入失敗: {e}")
                errors += 1
    
    print(f"✅ 匯入完成: {imported} 筆成功, {errors} 筆失敗, {skipped} 筆跳過")
    return imported

def import_tournament_participants(participants_data):
    """匯入賽事-參賽者關聯"""
    
    print("\n🏆 匯入賽事-參賽者關聯")
    print("=" * 40)
    
    imported = 0
    errors = 0
    
    with transaction.atomic():
        for tournament_id, team_id in participants_data:
            try:
                # 確認賽事和隊伍都存在
                tournament = Tournament.objects.get(id=tournament_id)
                team = Team.objects.get(id=team_id)
                
                # 添加參賽者（如果不存在）
                if not tournament.participants.filter(id=team_id).exists():
                    tournament.participants.add(team)
                    imported += 1
                    
            except Tournament.DoesNotExist:
                print(f"  ❌ 賽事 {tournament_id} 不存在")
                errors += 1
            except Team.DoesNotExist:
                print(f"  ❌ 隊伍 {team_id} 不存在")
                errors += 1
            except Exception as e:
                print(f"  ❌ 關聯 T{tournament_id}-{team_id} 失敗: {e}")
                errors += 1
    
    print(f"✅ 匯入完成: {imported} 筆成功, {errors} 筆失敗")
    return imported

def verify_completion():
    """驗證補充完成情況"""
    
    print(f"\n🔍 驗證補充結果")
    print("=" * 40)
    
    # 檢查小組-隊伍關聯
    total_group_teams = 0
    for group in Group.objects.all():
        team_count = group.teams.count()
        total_group_teams += team_count
        print(f"📋 {group.name}: {team_count} 支隊伍")
    
    # 檢查排名
    standings_count = Standing.objects.count()
    print(f"📊 排名記錄: {standings_count} 筆")
    
    # 檢查賽事參賽者
    total_participants = 0
    for tournament in Tournament.objects.all():
        participant_count = tournament.participants.count()
        total_participants += participant_count
        print(f"🏆 {tournament.name}: {participant_count} 支參賽隊伍")
    
    print(f"\n📈 總結:")
    print(f"  🔗 小組-隊伍關聯: {total_group_teams} 筆")
    print(f"  📊 排名記錄: {standings_count} 筆") 
    print(f"  🏆 賽事參賽者: {total_participants} 筆")
    
    return total_group_teams + standings_count + total_participants

def main():
    """主函數"""
    
    print("🔧 補齊關聯資料遷移")
    print("=" * 60)
    
    try:
        # 1. 從 Docker 取得資料
        docker_data = get_docker_missing_data()
        if not docker_data:
            print("❌ 無法取得 Docker 資料")
            return
        
        # 2. 匯入小組-隊伍關聯
        group_teams_imported = import_group_teams(docker_data['group_teams'])
        
        # 3. 匯入排名資料
        standings_imported = import_standings(docker_data['standings'], docker_data['standing_columns'])
        
        # 4. 匯入賽事-參賽者關聯
        participants_imported = import_tournament_participants(docker_data['tournament_participants'])
        
        # 5. 驗證結果
        total_imported = verify_completion()
        
        print(f"\n" + "=" * 60)
        print("🎉 關聯資料補充完成！")
        print(f"📊 本次匯入:")
        print(f"  🔗 小組-隊伍: {group_teams_imported} 筆")
        print(f"  📊 排名資料: {standings_imported} 筆")
        print(f"  🏆 參賽者關聯: {participants_imported} 筆")
        print(f"📈 目前總計: {total_imported} 筆關聯資料")
        
    except Exception as e:
        print(f"❌ 補充過程發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
