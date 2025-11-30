#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自動計算排名：基於比賽結果自動生成 Standing 資料
"""

import os

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

from tournaments.models import Tournament, Team, Match, Standing, Group
from django.db import transaction

def calculate_standings_for_tournament(tournament):
    """為特定賽事計算排名"""
    
    print(f"📊 計算 {tournament.name} 的排名...")
    
    # 取得所有小組
    groups = Group.objects.filter(tournament=tournament)
    print(f"  📋 找到 {groups.count()} 個小組")
    
    standings_created = 0
    
    with transaction.atomic():
        for group in groups:
            print(f"\n  📋 處理小組: {group.name}")
            
            # 取得小組中的所有隊伍
            teams = group.teams.all()
            print(f"    👥 小組中有 {teams.count()} 支隊伍")
            
            for team in teams:
                print(f"    👤 處理隊伍: {team.name}")
                
                # 檢查是否已存在排名記錄
                existing_standing = Standing.objects.filter(
                    tournament=tournament,
                    team=team,
                    group=group
                ).first()
                
                if existing_standing:
                    print(f"      ⚠️ 排名記錄已存在，跳過")
                    continue
                
                # 統計該隊伍在該小組的比賽結果
                # 作為 team1 的比賽
                matches_as_team1 = Match.objects.filter(
                    tournament=tournament,
                    team1=team,
                    status='completed'
                )
                
                # 作為 team2 的比賽  
                matches_as_team2 = Match.objects.filter(
                    tournament=tournament,
                    team2=team,
                    status='completed'
                )
                
                wins = 0
                losses = 0
                draws = 0
                
                # 計算作為 team1 的結果
                for match in matches_as_team1:
                    if match.winner_id == team.id:
                        wins += 1
                    elif match.winner_id is None:
                        draws += 1
                    elif match.winner_id:  # 對手獲勝
                        losses += 1
                
                # 計算作為 team2 的結果
                for match in matches_as_team2:
                    if match.winner_id == team.id:
                        wins += 1
                    elif match.winner_id is None:
                        draws += 1
                    elif match.winner_id:  # 對手獲勝
                        losses += 1
                
                # 計算分數 (通常是 勝場 * 3 + 平場 * 1)
                points = wins * 3 + draws * 1
                
                print(f"      📊 戰績: {wins}勝 {losses}負 {draws}平 = {points}分")
                
                # 創建排名記錄
                try:
                    standing = Standing.objects.create(
                        tournament=tournament,
                        team=team,
                        group=group,
                        wins=wins,
                        losses=losses,
                        draws=draws,
                        points=points
                    )
                    standings_created += 1
                    print(f"      ✅ 排名記錄創建成功")
                    
                except Exception as e:
                    print(f"      ❌ 創建排名失敗: {e}")
    
    return standings_created

def recalculate_all_standings():
    """重新計算所有賽事的排名"""
    
    print("🔄 自動計算所有排名資料")
    print("=" * 60)
    
    # 清空現有排名
    existing_count = Standing.objects.count()
    if existing_count > 0:
        print(f"🗑️ 清空現有的 {existing_count} 筆排名記錄...")
        Standing.objects.all().delete()
    
    total_created = 0
    
    # 處理所有賽事
    tournaments = Tournament.objects.all()
    print(f"🏆 找到 {tournaments.count()} 個賽事")
    
    for tournament in tournaments:
        created = calculate_standings_for_tournament(tournament)
        total_created += created
    
    return total_created

def verify_standings():
    """驗證排名計算結果"""
    
    print(f"\n🔍 驗證排名結果")
    print("=" * 40)
    
    standings = Standing.objects.all()
    print(f"📊 總排名記錄: {standings.count()} 筆")
    
    if standings.exists():
        print(f"\n📋 各小組排名:")
        
        for tournament in Tournament.objects.all():
            print(f"\n🏆 {tournament.name}:")
            
            groups = Group.objects.filter(tournament=tournament)
            for group in groups:
                print(f"\n  📋 {group.name} 排名:")
                
                group_standings = Standing.objects.filter(
                    tournament=tournament,
                    group=group
                ).order_by('-points', '-wins', 'losses')
                
                for i, standing in enumerate(group_standings, 1):
                    print(f"    {i}. {standing.team.name}: {standing.points}分 "
                          f"({standing.wins}勝{standing.losses}負{standing.draws}平)")
    
    return standings.count()

def check_matches_status():
    """檢查比賽狀態"""
    
    print(f"\n📊 比賽狀態統計")
    print("=" * 30)
    
    total_matches = Match.objects.count()
    completed_matches = Match.objects.filter(status='completed').count()
    ongoing_matches = Match.objects.filter(status='ongoing').count()
    scheduled_matches = Match.objects.filter(status='scheduled').count()
    
    print(f"總比賽: {total_matches}")
    print(f"已完成: {completed_matches}")
    print(f"進行中: {ongoing_matches}")
    print(f"已排程: {scheduled_matches}")
    
    return completed_matches

def main():
    """主函數"""
    
    print("🎯 自動計算排名系統")
    print("=" * 80)
    
    try:
        # 1. 檢查比賽狀態
        completed_matches = check_matches_status()
        
        if completed_matches == 0:
            print("\n⚠️ 沒有已完成的比賽，無法計算排名")
            return
        
        # 2. 重新計算排名
        total_created = recalculate_all_standings()
        
        # 3. 驗證結果
        final_count = verify_standings()
        
        print(f"\n" + "=" * 80)
        print("🎉 自動排名計算完成！")
        print(f"📊 基於 {completed_matches} 場已完成比賽")
        print(f"📋 創建了 {total_created} 筆排名記錄")
        print(f"✅ 最終驗證: {final_count} 筆排名資料")
        
        if total_created > 0:
            print("🚀 排名資料現在完全自動化生成！")
        else:
            print("⚠️ 可能需要檢查比賽資料或小組設定")
        
    except Exception as e:
        print(f"❌ 自動計算失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
