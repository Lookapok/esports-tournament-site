from django.core.management.base import BaseCommand
import json
from tournaments.models import Tournament, Team, Player, Match, Game, Group, Standing
from django.db import transaction
from django.utils.dateparse import parse_date, parse_datetime
from django.utils import timezone
from datetime import datetime

class Command(BaseCommand):
    help = '匯入錦標賽資料從 production_data.json'

    def parse_datetime_flexible(self, datetime_string):
        """靈活解析日期時間，支援多種格式"""
        if not datetime_string:
            return None
        
        try:
            # 嘗試解析 datetime 格式
            dt = parse_datetime(datetime_string)
            if dt:
                return dt
        except:
            pass
        
        try:
            # 嘗試解析純日期格式，轉為 datetime
            date_obj = parse_date(datetime_string)
            if date_obj:
                return timezone.make_aware(datetime.combine(date_obj, datetime.min.time()))
        except:
            pass
            
        # 如果都失敗，使用當前時間
        self.stdout.write(f"⚠️ 無法解析日期時間: {datetime_string}，使用當前時間")
        return timezone.now()

    def handle(self, *args, **options):
        try:
            self.stdout.write("🔄 開始匯入錦標賽資料...")
            
            # 檢查檔案是否存在
            import os
            if not os.path.exists('production_data.json'):
                self.stdout.write(self.style.ERROR("❌ production_data.json 檔案不存在！"))
                return
            
            # 顯示檔案資訊
            file_size = os.path.getsize('production_data.json')
            self.stdout.write(f"📁 檔案大小: {file_size} bytes")
            
            # 讀取資料檔案
            with open('production_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 顯示資料統計
            tournaments = data.get('tournaments', [])
            teams = data.get('teams', [])
            players = data.get('players', [])
            matches = data.get('matches', [])
            
            self.stdout.write(f"📊 資料統計:")
            self.stdout.write(f"  - 錦標賽: {len(tournaments)} 筆")
            self.stdout.write(f"  - 隊伍: {len(teams)} 筆")
            self.stdout.write(f"  - 選手: {len(players)} 筆")
            self.stdout.write(f"  - 比賽: {len(matches)} 筆")
            
            if len(tournaments) == 0:
                self.stdout.write(self.style.WARNING("⚠️ 沒有錦標賽資料可匯入"))
                return
            
            # 使用事務確保資料完整性
            with transaction.atomic():
                # 匯入錦標賽
                self.stdout.write("🏆 開始匯入錦標賽...")
                tournament_count = 0
                for item in tournaments:
                    try:
                        tournament, created = Tournament.objects.get_or_create(
                            id=item['id'],
                            defaults={
                                'name': item['name'],
                                'game': item['game'],
                                'start_date': self.parse_datetime_flexible(item.get('start_date')),
                                'end_date': self.parse_datetime_flexible(item.get('end_date')),
                                'rules': item.get('rules', ''),
                                'status': item.get('status', 'upcoming'),
                                'format': item.get('format', 'single_elimination')
                            }
                        )
                        tournament_count += 1
                        if created:
                            self.stdout.write(f"  ✅ 創建錦標賽: {tournament.name}")
                        else:
                            self.stdout.write(f"  ℹ️ 錦標賽已存在: {tournament.name}")
                    except Exception as e:
                        self.stdout.write(f"  ❌ 錦標賽匯入失敗: {item.get('name', 'Unknown')} - {str(e)}")
                        raise  # 重新拋出錯誤以觸發回滾
                
                self.stdout.write(f"🏆 錦標賽匯入完成: {tournament_count} 筆")
                
                # 匯入隊伍
                for item in data.get('teams', []):
                    Team.objects.get_or_create(
                        id=item['id'],
                        defaults={
                            'name': item['name'],
                            'logo': item.get('logo', '')
                        }
                    )
                
                # 匯入選手
                for item in data.get('players', []):
                    try:
                        team = Team.objects.get(id=item['team_id']) if item['team_id'] else None
                    except Team.DoesNotExist:
                        team = None
                    
                    Player.objects.get_or_create(
                        id=item['id'],
                        defaults={
                            'nickname': item['nickname'],
                            'team': team,
                            'avatar': item.get('avatar', ''),
                            'role': item.get('role', '')
                        }
                    )
                
                # 匯入小組
                for item in data.get('groups', []):
                    try:
                        tournament = Tournament.objects.get(id=item['tournament_id'])
                        Group.objects.get_or_create(
                            id=item['id'],
                            defaults={
                                'tournament': tournament,
                                'name': item['name']
                            }
                        )
                    except Tournament.DoesNotExist:
                        continue
                
                # 匯入比賽
                for item in data.get('matches', []):
                    try:
                        tournament = Tournament.objects.get(id=item['tournament_id'])
                        team1 = Team.objects.get(id=item['team1_id']) if item['team1_id'] else None
                        team2 = Team.objects.get(id=item['team2_id']) if item['team2_id'] else None
                        winner = Team.objects.get(id=item['winner_id']) if item['winner_id'] else None
                        
                        Match.objects.get_or_create(
                            id=item['id'],
                            defaults={
                                'tournament': tournament,
                                'round_number': item.get('round_number', 1),
                                'map': item.get('map', ''),
                                'team1': team1,
                                'team2': team2,
                                'team1_score': item.get('team1_score', 0),
                                'team2_score': item.get('team2_score', 0),
                                'winner': winner,
                                'match_time': parse_datetime(item['match_time']) if item.get('match_time') else None,
                                'status': item.get('status', 'scheduled'),
                                'is_lower_bracket': item.get('is_lower_bracket', False)
                            }
                        )
                    except (Tournament.DoesNotExist, Team.DoesNotExist):
                        continue
                
                # 匯入遊戲
                for item in data.get('games', []):
                    try:
                        match = Match.objects.get(id=item['match_id'])
                        winner = Team.objects.get(id=item['winner_id']) if item['winner_id'] else None
                        
                        Game.objects.get_or_create(
                            id=item['id'],
                            defaults={
                                'match': match,
                                'map_number': item.get('map_number', 1),
                                'map_name': item.get('map_name', ''),
                                'team1_score': item.get('team1_score', 0),
                                'team2_score': item.get('team2_score', 0),
                                'winner': winner
                            }
                        )
                    except (Match.DoesNotExist, Team.DoesNotExist):
                        continue
                
                # 匯入積分榜
                self.stdout.write("🏆 開始匯入積分榜...")
                standings_imported = 0
                for item in data.get('standings', []):
                    try:
                        tournament = Tournament.objects.get(id=item['tournament_id'])
                        team = Team.objects.get(id=item['team_id'])
                        group = Group.objects.get(id=item['group_id']) if item.get('group_id') else None
                        
                        # 使用 unique_together 約束進行匯入
                        standing, created = Standing.objects.get_or_create(
                            tournament=tournament,
                            team=team,
                            defaults={
                                'group': group,
                                'wins': item.get('wins', 0),
                                'losses': item.get('losses', 0),
                                'draws': item.get('draws', 0),
                                'points': item.get('points', 0)
                            }
                        )
                        if created:
                            standings_imported += 1
                        else:
                            # 更新現有記錄
                            standing.group = group
                            standing.wins = item.get('wins', 0)
                            standing.losses = item.get('losses', 0)
                            standing.draws = item.get('draws', 0)
                            standing.points = item.get('points', 0)
                            standing.save()
                            standings_imported += 1
                            
                    except Tournament.DoesNotExist:
                        self.stdout.write(f"  ⚠️ 找不到錦標賽 ID: {item.get('tournament_id')}")
                        continue
                    except Team.DoesNotExist:
                        self.stdout.write(f"  ⚠️ 找不到隊伍 ID: {item.get('team_id')}")
                        continue
                    except Group.DoesNotExist:
                        self.stdout.write(f"  ⚠️ 找不到分組 ID: {item.get('group_id')}")
                        continue
                    except Exception as e:
                        self.stdout.write(f"  ❌ 匯入積分榜記錄失敗: {str(e)}")
                        continue
                
                self.stdout.write(f"🏆 積分榜匯入完成: {standings_imported} 筆")
            
            self.stdout.write(self.style.SUCCESS("🎉 資料匯入完成！"))
            
            # 驗證匯入結果
            self.stdout.write("🔍 驗證匯入結果...")
            tournament_count = Tournament.objects.count()
            team_count = Team.objects.count()
            player_count = Player.objects.count()
            match_count = Match.objects.count()
            standing_count = Standing.objects.count()
            
            self.stdout.write(f"📊 最終統計:")
            self.stdout.write(f"  - 錦標賽: {tournament_count} 筆")
            self.stdout.write(f"  - 隊伍: {team_count} 筆")
            self.stdout.write(f"  - 選手: {player_count} 筆")
            self.stdout.write(f"  - 比賽: {match_count} 筆")
            self.stdout.write(f"  - 積分榜: {standing_count} 筆")
            
            if tournament_count > 0:
                self.stdout.write(self.style.SUCCESS("✅ 資料匯入驗證成功！"))
            else:
                self.stdout.write(self.style.ERROR("❌ 資料匯入驗證失敗：沒有錦標賽資料"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ 匯入失敗: {str(e)}"))
            import traceback
            self.stdout.write(f"詳細錯誤: {traceback.format_exc()}")
