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
            
            # 讀取資料檔案
            with open('production_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            with transaction.atomic():
                # 匯入錦標賽
                for item in data.get('tournaments', []):
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
                for item in data.get('standings', []):
                    try:
                        tournament = Tournament.objects.get(id=item['tournament_id'])
                        team = Team.objects.get(id=item['team_id'])
                        group = Group.objects.get(id=item['group_id']) if item['group_id'] else None
                        
                        Standing.objects.get_or_create(
                            id=item['id'],
                            defaults={
                                'tournament': tournament,
                                'team': team,
                                'group': group,
                                'wins': item.get('wins', 0),
                                'losses': item.get('losses', 0),
                                'draws': item.get('draws', 0),
                                'points': item.get('points', 0)
                            }
                        )
                    except (Tournament.DoesNotExist, Team.DoesNotExist, Group.DoesNotExist):
                        continue
            
            self.stdout.write(self.style.SUCCESS("🎉 資料匯入完成！"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ 匯入失敗: {str(e)}"))
