# tournaments/admin.py

from django.contrib import admin, messages
from .models import Tournament, Team, Player, Match, Group, Standing, Game, PlayerGameStat
from .logic import generate_round_robin_matches, generate_swiss_round_matches, generate_single_elimination_matches, generate_double_elimination_matches
import logging

# 取得業務邏輯專用的日誌記錄器
business_logger = logging.getLogger('tournaments.business')

# --- Inline 設定 ---

class PlayerGameStatInline(admin.TabularInline):
    model = PlayerGameStat
    extra = 1
    autocomplete_fields = ['player', 'team'] 

class GameInline(admin.TabularInline):
    model = Game
    extra = 1
    fields = ('map_number', 'map_name', 'team1_score', 'team2_score', 'winner')

# --- ModelAdmin 設定 (已為主要模型加入 ID 顯示) ---

# 移除重複的 generate_matches_action 定義

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'format', 'status') # <--- 加上 id
    list_filter = ('format', 'status')
    # actions 將在後面定義 generate_matches_action 後加入
    search_fields = ('name',)

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',) # <--- 加上 id
    search_fields = ('name',)

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('id', 'nickname', 'team', 'role') # <--- 加上 id
    list_filter = ('role', 'team') 
    search_fields = ('nickname',)
    autocomplete_fields = ['team'] 

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('id', '__str__', 'tournament', 'status', 'team1_score', 'team2_score', 'winner') # <--- 加上比分和 id
    list_filter = ('tournament', 'status', 'winner')
    search_fields = ('team1__name', 'team2__name')
    list_display_links = ('id', '__str__') # <-- 讓 id 也可以點擊
    inlines = [GameInline]
    
    # 新增自定義欄位顯示
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('team1', 'team2', 'winner', 'tournament')

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('id', '__str__', 'map_name', 'winner') # <--- 加上 id
    list_filter = ('match__tournament',)
    inlines = [PlayerGameStatInline]

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'tournament') # <--- 加上 id
    filter_horizontal = ('teams',)

@admin.register(Standing)
class StandingAdmin(admin.ModelAdmin):
    list_display = ('id', 'team', 'tournament', 'wins', 'losses', 'points') # <--- 加上 id
    list_filter = ('tournament',)

@admin.register(PlayerGameStat)
class PlayerGameStatAdmin(admin.ModelAdmin):
    list_display = ('id', '__str__', 'kills', 'deaths', 'assists', 'acs')
    list_filter = ('game__match__tournament',)
    search_fields = ('player__nickname',)

    # tournaments/admin.py

@admin.action(description='為選定的賽事自動產生賽程')
def generate_matches_action(modeladmin, request, queryset):
    for tournament in queryset:
        # 記錄賽程生成開始
        business_logger.info('Tournament Match Generation Started', extra={
            'event_type': 'match_generation_start',
            'tournament_id': tournament.id,
            'tournament_name': tournament.name,
            'tournament_format': tournament.format,
            'participant_count': tournament.participants.count(),
            'user': str(request.user),
        })
        # --- 分組循環邏輯 ---
        if tournament.format == 'round_robin':
            # 1. (重要) 先為所有參賽隊伍建立空的積分榜紀錄
            # 不刪除現有的 Standing，而是確保所有參賽隊伍都有積分記錄
            for team in tournament.participants.all():
                # 檢查是否已存在，不存在才建立新的
                if not Standing.objects.filter(tournament=tournament, team=team).exists():
                    Standing.objects.create(tournament=tournament, team=team)
            
            # 同步 Group.teams 和 Standing.group 的關係 (如果有分組資料的話)
            groups = tournament.groups.all()
            for group in groups:
                for team in group.teams.all():
                    # 更新對應的 Standing 記錄的分組資訊
                    standing = Standing.objects.filter(tournament=tournament, team=team).first()
                    if standing and standing.group != group:
                        standing.group = group
                        standing.save()

            # 2. 呼叫 logic 函式來產生比賽
            count = generate_round_robin_matches(tournament)
            business_logger.info('Round Robin Matches Generated', extra={
                'event_type': 'match_generation_success',
                'tournament_id': tournament.id,
                'tournament_format': 'round_robin',
                'matches_created': count,
            })
            modeladmin.message_user(request, f"已成功為循環賽 '{tournament.name}' 產生了 {count} 場比賽。", messages.SUCCESS)

        # --- 瑞士輪邏輯 (維持不變) ---
        elif tournament.format == 'swiss':
            if not Standing.objects.filter(tournament=tournament).exists():
                for team in tournament.participants.all():
                    Standing.objects.create(tournament=tournament, team=team)
            count = generate_swiss_round_matches(tournament)
            business_logger.info('Swiss Round Matches Generated', extra={
                'event_type': 'match_generation_success',
                'tournament_id': tournament.id,
                'tournament_format': 'swiss',
                'matches_created': count,
            })
            modeladmin.message_user(request, f"已為瑞士輪 '{tournament.name}' 產生了 {count} 場新比賽。", messages.SUCCESS)

        # --- 單淘汰賽邏輯 ---
        elif tournament.format == 'single_elimination':
            # 檢查是否有參賽隊伍
            if not tournament.participants.exists():
                modeladmin.message_user(request, f"賽事 '{tournament.name}' 沒有參賽隊伍，無法產生賽程。", messages.WARNING)
                continue
                
            count = generate_single_elimination_matches(tournament)
            business_logger.info('Single Elimination Matches Generated', extra={
                'event_type': 'match_generation_success',
                'tournament_id': tournament.id,
                'tournament_format': 'single_elimination',
                'matches_created': count,
            })
            modeladmin.message_user(request, f"已成功為單淘汰賽 '{tournament.name}' 產生了 {count} 場比賽。", messages.SUCCESS)

        # --- 雙淘汰賽邏輯 ---
        elif tournament.format == 'double_elimination':
            # 檢查是否有參賽隊伍
            if not tournament.participants.exists():
                modeladmin.message_user(request, f"賽事 '{tournament.name}' 沒有參賽隊伍，無法產生賽程。", messages.WARNING)
                continue
                
            count = generate_double_elimination_matches(tournament)
            business_logger.info('Double Elimination Matches Generated', extra={
                'event_type': 'match_generation_success',
                'tournament_id': tournament.id,
                'tournament_format': 'double_elimination',
                'matches_created': count,
            })
            modeladmin.message_user(request, f"已成功為雙淘汰賽 '{tournament.name}' 產生了 {count} 場比賽。", messages.SUCCESS)

        # --- 其他賽制 ---
        else:
            modeladmin.message_user(request, f"賽事 '{tournament.name}' 的賽制 ({tournament.get_format_display()}) 不支援自動產生賽程。", messages.WARNING)

# 檢查和修復分組資料
@admin.action(description='檢查和修復分組資料')
def fix_group_data_action(modeladmin, request, queryset):
    """檢查和修復分組資料的一致性"""
    for tournament in queryset:
        issues_found = []
        
        # 檢查是否有隊伍在多個分組中
        teams_in_groups = {}
        for group in tournament.groups.all():
            for team in group.teams.all():
                if team.id not in teams_in_groups:
                    teams_in_groups[team.id] = []
                teams_in_groups[team.id].append(group.name)
        
        # 找出在多個分組的隊伍
        duplicate_teams = {team_id: groups for team_id, groups in teams_in_groups.items() if len(groups) > 1}
        
        if duplicate_teams:
            for team_id, groups in duplicate_teams.items():
                team = Team.objects.get(id=team_id)
                issues_found.append(f"隊伍 '{team.name}' 同時在分組: {', '.join(groups)}")
                
            # 提供修復選項
            if 'fix' in request.POST:
                # 自動修復：每個隊伍只保留在第一個分組
                for team_id, groups in duplicate_teams.items():
                    team = Team.objects.get(id=team_id)
                    # 移除除了第一個分組之外的所有分組
                    groups_to_remove = tournament.groups.filter(name__in=groups[1:])
                    for group in groups_to_remove:
                        group.teams.remove(team)
                
                modeladmin.message_user(
                    request, 
                    f"已修復 {len(duplicate_teams)} 個重複分組問題", 
                    messages.SUCCESS
                )
            else:
                # 只報告問題
                error_msg = "發現分組問題:\n" + "\n".join(issues_found)
                error_msg += "\n\n要修復這些問題，請在選擇此動作後勾選下方的修復選項。"
                modeladmin.message_user(request, error_msg, messages.WARNING)
        else:
            modeladmin.message_user(request, f"賽事 '{tournament.name}' 的分組資料正常", messages.SUCCESS)

# 將 action 加入 TournamentAdmin
TournamentAdmin.actions = [generate_matches_action, fix_group_data_action]

# --- 比賽管理 Admin Actions ---

@admin.action(description='設置隊伍1為勝者（自動根據比分判斷）')
def set_team1_as_winner_action(modeladmin, request, queryset):
    """設置選定比賽的隊伍1為勝者"""
    updated_count = 0
    for match in queryset:
        if match.team1 and match.team2:
            old_winner = match.winner
            match.winner = match.team1
            match.status = 'completed'  # 自動設為已完成
            match.save()
            updated_count += 1
            
            # 記錄變更
            business_logger.info('Match Winner Set Manually', extra={
                'event_type': 'match_winner_set',
                'match_id': match.id,
                'team1': match.team1.name,
                'team2': match.team2.name,
                'winner': match.winner.name,
                'old_winner': old_winner.name if old_winner else None,
                'user': str(request.user),
            })
    
    modeladmin.message_user(
        request, 
        f"已成功設置 {updated_count} 場比賽的隊伍1為勝者，並自動觸發積分計算。", 
        messages.SUCCESS
    )

@admin.action(description='設置隊伍2為勝者（自動根據比分判斷）')
def set_team2_as_winner_action(modeladmin, request, queryset):
    """設置選定比賽的隊伍2為勝者"""
    updated_count = 0
    for match in queryset:
        if match.team1 and match.team2:
            old_winner = match.winner
            match.winner = match.team2
            match.status = 'completed'  # 自動設為已完成
            match.save()
            updated_count += 1
            
            # 記錄變更
            business_logger.info('Match Winner Set Manually', extra={
                'event_type': 'match_winner_set',
                'match_id': match.id,
                'team1': match.team1.name,
                'team2': match.team2.name,
                'winner': match.winner.name,
                'old_winner': old_winner.name if old_winner else None,
                'user': str(request.user),
            })
    
    modeladmin.message_user(
        request, 
        f"已成功設置 {updated_count} 場比賽的隊伍2為勝者，並自動觸發積分計算。", 
        messages.SUCCESS
    )

@admin.action(description='根據比分自動設置勝者')
def auto_set_winner_by_score_action(modeladmin, request, queryset):
    """根據比分自動設置勝者"""
    updated_count = 0
    no_score_count = 0
    tie_count = 0
    
    for match in queryset:
        if match.team1_score is None or match.team2_score is None:
            no_score_count += 1
            continue
            
        if match.team1_score == match.team2_score:
            tie_count += 1
            continue
            
        old_winner = match.winner
        
        if match.team1_score > match.team2_score:
            match.winner = match.team1
        else:
            match.winner = match.team2
            
        match.status = 'completed'
        match.save()
        updated_count += 1
        
        # 記錄變更
        business_logger.info('Match Winner Auto-Set by Score', extra={
            'event_type': 'match_winner_auto_set',
            'match_id': match.id,
            'team1': match.team1.name,
            'team2': match.team2.name,
            'team1_score': match.team1_score,
            'team2_score': match.team2_score,
            'winner': match.winner.name,
            'old_winner': old_winner.name if old_winner else None,
            'user': str(request.user),
        })
    
    messages_list = []
    if updated_count > 0:
        messages_list.append(f"成功設置 {updated_count} 場比賽的勝者")
    if no_score_count > 0:
        messages_list.append(f"{no_score_count} 場比賽沒有比分，跳過")
    if tie_count > 0:
        messages_list.append(f"{tie_count} 場比賽平手，需要手動處理")
        
    modeladmin.message_user(
        request, 
        "；".join(messages_list) + "。", 
        messages.SUCCESS if updated_count > 0 else messages.WARNING
    )

@admin.action(description='清除勝者設置（重設比賽狀態）')
def clear_winner_action(modeladmin, request, queryset):
    """清除選定比賽的勝者設置"""
    updated_count = 0
    for match in queryset:
        if match.winner:
            old_winner = match.winner
            match.winner = None
            match.status = 'scheduled'  # 重設為預定狀態
            match.save()
            updated_count += 1
            
            # 記錄變更
            business_logger.info('Match Winner Cleared', extra={
                'event_type': 'match_winner_cleared',
                'match_id': match.id,
                'team1': match.team1.name,
                'team2': match.team2.name,
                'old_winner': old_winner.name,
                'user': str(request.user),
            })
    
    modeladmin.message_user(
        request, 
        f"已成功清除 {updated_count} 場比賽的勝者設置，並自動觸發積分重算。", 
        messages.SUCCESS
    )

# 將 actions 加入 MatchAdmin
MatchAdmin.actions = [
    set_team1_as_winner_action, 
    set_team2_as_winner_action, 
    auto_set_winner_by_score_action,
    clear_winner_action
]