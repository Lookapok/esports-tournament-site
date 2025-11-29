from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.db.models import Q, Prefetch
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.core.paginator import Paginator
from collections import defaultdict
import random
import math
from django.contrib import messages
from django.http import JsonResponse
from .models import Tournament, Match, Team, Player, PlayerGameStat, Group, Standing
from .forms import TournamentCreationStep1Form, TeamCreationStep2Form
from .tables import StatsTable
from .logic import generate_round_robin_matches, generate_swiss_round_matches, generate_single_elimination_matches, generate_double_elimination_matches

# ===== 權限檢查函數 =====
def is_superuser(user):
    """檢查用戶是否為超級管理員"""
    return user.is_superuser

# tournaments/views.py

def tournament_list(request):
    try:
        # ===== 優化的快取策略 =====
        # 使用更細緻的快取金鑰，包含版本資訊
        from django.conf import settings
        cache_version = getattr(settings, 'CACHE_VERSION', 1)
        cache_key = f'tournament_list_v{cache_version}'
        
        # 檢查快取（添加錯誤處理）
        try:
            cached_result = cache.get(cache_key)
            if cached_result:
                return render(request, 'tournaments/tournament_list.html', cached_result)
        except Exception:
            # 快取失敗時忽略並繼續
            pass
        
        # 1. 極度優化的賽事查詢，只載入必要欄位
        tournaments = Tournament.objects.select_related().only(
            'id', 'name', 'start_date', 'end_date', 'status', 'format'
        ).order_by('-start_date')
        
        # 2. 極度優化的即將到來比賽查詢
        upcoming_matches = Match.objects.select_related(
            'tournament', 'team1', 'team2'
        ).only(
            'id', 'match_time', 'status',
            'tournament__name', 'team1__name', 'team2__name'
        ).filter(
            status='scheduled',
            match_time__gte=timezone.now()
        ).order_by('match_time')[:3]  # 減少到3場以加快載入

        context = {
            'tournaments': tournaments,
            'upcoming_matches': upcoming_matches,
        }
        
        # 快取結果 10 分鐘，賽事列表變動較少（添加錯誤處理）
        try:
            cache.set(cache_key, context, 600)
        except Exception:
            # 快取失敗時忽略
            pass
        
        return render(request, 'tournaments/tournament_list.html', context)
    
    except Exception as e:
        # 如果所有操作都失敗，返回簡單的空頁面
        context = {
            'tournaments': Tournament.objects.none(),
            'upcoming_matches': Match.objects.none(),
            'error_message': f'資料載入中，請稍後再試。'
        }
        return render(request, 'tournaments/tournament_list.html', context)

def tournament_detail(request, pk):
    try:
        # ===== 優化的快取策略 =====
        # 更精確的快取金鑰，避免衝突
        page_number = request.GET.get('page', '1')
        from django.conf import settings
        cache_version = getattr(settings, 'CACHE_VERSION', 1)
        cache_key = f'tournament_detail_v{cache_version}_{pk}_page_{page_number}'
        
        # 檢查快取（添加錯誤處理）
        try:
            cached_result = cache.get(cache_key)
            if cached_result:
                return render(request, 'tournaments/tournament_detail.html', cached_result)
        except Exception:
            # 快取失敗時忽略
            pass
        
        # 分層載入數據，避免一次載入過多數據導致頁面載入緩慢
        
        # 1. 極度優化的賽事基本信息載入
        tournament = get_object_or_404(
            Tournament.objects.select_related().only(
                'id', 'name', 'format', 'status', 'start_date', 'end_date'
            ), 
            pk=pk
        )
        
        context = {'tournament': tournament}
        
        # 2. 根據賽制分別極度優化數據載入
        if tournament.format == 'round_robin':
            # 分組循環：按分組分頁顯示（A組、B組、C組、D組等）
            from django.core.paginator import Paginator
            
            try:
                # 只載入必要的分組資料，按名稱排序
                groups = tournament.groups.order_by('name')
                
                # 按分組分頁（每頁顯示一個分組）
                paginator = Paginator(groups, 1)
                page_number = request.GET.get('page', 1)
                page_groups = paginator.get_page(page_number)
                
                # 取得當前頁面的分組
                current_group = page_groups.object_list[0] if page_groups.object_list else None
                
                # --- [核心修正點] ---
                group_standings = []
                group_matches = []
                if current_group:
                    try:
                        # [新增] 查詢當前分組的積分榜 (Standing) 並進行排序
                        group_standings = Standing.objects.filter(
                            group=current_group
                        ).select_related('team').order_by('-points', '-wins', 'team__name')

                        # [優化] 為當前分組載入相關比賽的邏輯
                        group_matches = tournament.matches.select_related(
                            'team1', 'team2', 'winner'
                        ).only(
                            'id', 'team1__name', 'team2__name', 'winner__name', 
                            'team1_score', 'team2_score', 'status', 'match_time'
                        ).filter(
                            team1__in=current_group.teams.all(),
                            team2__in=current_group.teams.all()
                        ).order_by('id')[:50]
                    except Exception as e:
                        # 如果查詢失敗，使用空列表
                        group_standings = []
                        group_matches = []
                # --- [修正結束] ---

                context['groups'] = page_groups
                context['current_group'] = current_group
                context['group_matches'] = group_matches
                context['group_standings'] = group_standings
            
            except Exception as e:
                # 如果分組查詢失敗，顯示空內容
                context['groups'] = []
                context['current_group'] = None
                context['group_matches'] = []
                context['group_standings'] = []
                
        elif tournament.format == 'swiss':
            try:
                # 瑞士輪：極度優化積分榜和分頁比賽
                context['standings'] = tournament.standings.select_related('team').only(
                    'team__name', 'points', 'wins', 'losses', 'draws'
                ).order_by('-points', '-wins')[:20]  # 限制顯示前20名
                
                # 極度優化的分頁比賽（每頁15場以加快載入）
                from django.core.paginator import Paginator
                
                matches = tournament.matches.select_related('team1', 'team2', 'winner').only(
                    'id', 'round_number', 'team1__name', 'team2__name', 'winner__name',
                    'team1_score', 'team2_score', 'status', 'match_time'
                ).order_by('round_number', 'id')
                
                paginator = Paginator(matches, 15)  # 減少每頁數量
                page_number = request.GET.get('page', 1)
                page_matches = paginator.get_page(page_number)
                
                # 按輪次分組（僅針對當前頁面的比賽）
                rounds = defaultdict(list)
                for match in page_matches:
                    rounds[match.round_number].append(match)
                
                context['rounds'] = dict(rounds)
                context['page_matches'] = page_matches
            except Exception as e:
                context['standings'] = []
                context['rounds'] = {}
                context['page_matches'] = []
                
        else:  # Elimination (single/double)
            try:
                # 淘汰賽：極度優化分頁顯示比賽
                from django.core.paginator import Paginator
                
                matches = tournament.matches.select_related('team1', 'team2', 'winner').only(
                    'id', 'round_number', 'team1__name', 'team2__name', 'winner__name',
                    'team1_score', 'team2_score', 'status', 'match_time'
                ).order_by('round_number', 'id')
                
                paginator = Paginator(matches, 15)  # 減少每頁數量
                page_number = request.GET.get('page', 1)
                page_matches = paginator.get_page(page_number)
                
                # 按輪次分組（僅針對當前頁面的比賽）
                rounds = defaultdict(list)
                for match in page_matches:
                    rounds[match.round_number].append(match)
                
                context['rounds'] = dict(rounds)
                context['page_matches'] = page_matches
            except Exception as e:
                context['rounds'] = {}
                context['page_matches'] = []
        
        # 智能快取策略：根據賽事狀態和內容類型設定不同的過期時間
        if tournament.status == 'completed':
            # 已完成的賽事快取更久（30分鐘），因為數據不會改變
            cache_timeout = 1800
        elif tournament.status == 'ongoing':
            # 進行中的賽事快取時間中等（10分鐘），平衡即時性和性能
            cache_timeout = 600
        else:
            # 未開始的賽事快取時間較短（5分鐘），可能有變動
            cache_timeout = 300
        
        # 設定快取，包含錯誤處理
        try:
            cache.set(cache_key, context, cache_timeout)
        except Exception as e:
            # 快取失敗不應影響頁面正常顯示
            pass
        
        return render(request, 'tournaments/tournament_detail.html', context)
    
    except Exception as e:
        # 如果所有操作都失敗，返回一個帶錯誤訊息的簡單頁面
        context = {
            'tournament': None,
            'error_message': '錦標賽資料載入中，請稍後再試。'
        }
        return render(request, 'tournaments/tournament_detail.html', context)

def team_list(request):
    # ===== 優化的隊伍列表快取策略 =====
    from django.conf import settings
    cache_version = getattr(settings, 'CACHE_VERSION', 1)
    cache_key = f'team_list_v{cache_version}_all'  # 移除分頁，改為全部隊伍
    
    # 檢查快取
    cached_result = cache.get(cache_key)
    if cached_result:
        return render(request, 'tournaments/team_list.html', cached_result)
    
    # 1. 優化的隊伍查詢，載入所有隊伍
    teams = Team.objects.prefetch_related(
        Prefetch('players', queryset=Player.objects.only('id', 'nickname', 'role'))
    ).only('id', 'name', 'logo').order_by('name')
    
    context = {
        'teams': teams,  # 顯示所有隊伍
    }
    
    # 隊伍資料相對穩定，快取 15 分鐘
    try:
        cache.set(cache_key, context, 900)
    except Exception as e:
        print(f"隊伍列表快取設定失敗: {e}")
    
    return render(request, 'tournaments/team_list.html', context)

# tournaments/views.py

def team_detail(request, pk):
    team = get_object_or_404(Team, pk=pk)
    players = team.players.all()

    # --- 新增的邏輯：查詢歷史戰績 ---
    # 使用 Q 物件，查詢 team1 或 team2 是目前隊伍的所有比賽
    # .select_related() 用來優化查詢，一次性抓取關聯的隊伍資料
    # .order_by('-match_time') 讓最新的比賽顯示在最上面
    match_history = Match.objects.filter(
        Q(team1=team) | Q(team2=team),
        status='completed' # 只顯示已完成的比賽
    ).select_related('team1', 'team2', 'tournament').order_by('-match_time')
    # --------------------------------

    context = {
        'team': team,
        'players': players,
        'match_history': match_history, # 將歷史戰績傳給模板
    }

    return render(request, 'tournaments/team_detail.html', context)

def overall_stats(request):
    # --- [核心修正點] ---
    # 查詢路徑從 'match__tournament' 改為 'game__match__tournament'
    # 為了讓 tables.py 中的 LinkColumn 能運作，我們也需要預先載入 'game__match'
    stats_queryset = PlayerGameStat.objects.select_related(
        'player', 
        'team', 
        'game__match', 
        'game__match__tournament'
    ).all()
    # --------------------

    # --- 篩選邏輯 (維持不變) ---
    selected_team_id = request.GET.get('team')
    player_name_query = request.GET.get('player_name')

    if selected_team_id:
        # 篩選條件也要跟著更新
        stats_queryset = stats_queryset.filter(team__id=selected_team_id)

    if player_name_query:
        stats_queryset = stats_queryset.filter(player__nickname__icontains=player_name_query)

    # 建立 Table 的實例
    table = StatsTable(stats_queryset) # <-- 使用修正後的查詢結果

    # 告訴 Table 要根據 URL 中的 "sort" 參數來排序
    table.order_by = request.GET.get("sort", "-acs") # 預設按 ACS 降序排列
    
    # 準備篩選器下拉選單要用的所有隊伍資料
    all_teams = Team.objects.all()

    context = {
        'table': table,
        'all_teams': all_teams,
        # 讓前端能保留篩選狀態
        'selected_team_id': int(selected_team_id) if selected_team_id else None,
        'player_name_query': player_name_query,
    }

    return render(request, 'tournaments/overall_stats.html', context)

# This is the function that was missing
def tournament_stats(request, pk):
    tournament = get_object_or_404(Tournament, pk=pk)
    stats = PlayerGameStat.objects.filter(game__tournament=tournament).select_related('player', 'team')
    context = {
        'tournament': tournament,
        'stats': stats,
    }
    return render(request, 'tournaments/tournament_stats.html', context)

# 在檔案最下方新增這個函式
def register(request):
    # 如果使用者是透過 POST 方式提交資料 (也就是按下了註冊按鈕)
    if request.method == 'POST':
        # 用提交的資料建立一個 UserCreationForm 的實體
        form = UserCreationForm(request.POST)
        # 檢查表單資料是否合法 (例如：密碼是否一致)
        if form.is_valid():
            # 如果合法，就將新使用者存入資料庫
            user = form.save()
            # 註冊成功後，自動幫使用者登入
            login(request, user)
            # 將使用者重新導向到網站首頁
            return redirect('tournament_list')
    # 如果使用者是透過 GET 方式來到此頁面 (第一次瀏覽)
    else:
        # 建立一個空白的表單
        form = UserCreationForm()

    # 將表單物件傳遞給 HTML 模板
    return render(request, 'registration/register.html', {'form': form})

@login_required
@user_passes_test(is_superuser, login_url='/admin/')
def dashboard(request):
    return render(request, 'registration/dashboard.html')

def custom_logout(request):
    logout(request)
    return redirect('tournament_list')

# tournaments/views.py

@login_required
@user_passes_test(is_superuser, login_url='/admin/')
def tournament_create_step1(request):
    if request.method == 'POST':
        form = TournamentCreationStep1Form(request.POST)
        if form.is_valid():
            step1_data = form.cleaned_data

            # --- 主要修正點在這裡 ---
            # 我們要把所有資料都包在一個 'step1' 的字典裡
            request.session['wizard_data'] = {
                'step1': {
                    'name': step1_data['name'],
                    'game': step1_data['game'],
                    'format': step1_data['format'],
                    'rules': step1_data['rules'],
                    'start_date': step1_data['start_date'].isoformat(),
                    'end_date': step1_data['end_date'].isoformat(),
                }
            }
            # -------------------------

            return redirect('tournament_create_step2')
    else:
        # 檢查 session 中是否有舊資料，方便使用者返回上一步修改
        wizard_data = request.session.get('wizard_data', {})
        step1_data = wizard_data.get('step1', None)
        form = TournamentCreationStep1Form(initial=step1_data)

    return render(request, 'tournaments/wizard_step1.html', {'form': form})

# tournaments/views.py

# 在檔案最下方新增這個函式
# tournaments/views.py

@login_required
@user_passes_test(is_superuser, login_url='/admin/')
def tournament_create_step2(request):
    wizard_data = request.session.get('wizard_data', {})
    # 如果沒有第一步的資料，就強制返回第一步
    if 'step1' not in wizard_data:
        return redirect('tournament_create_step1')

    if request.method == 'POST':
        form = TeamCreationStep2Form(request.POST)
        if form.is_valid():
            teams_text = form.cleaned_data['teams_text']
            wizard_data['step2'] = {
                'teams': [name.strip() for name in teams_text.splitlines() if name.strip()]
            }
            request.session['wizard_data'] = wizard_data
            return redirect('tournament_create_step3')
    else:
        # 檢查 session 中是否有舊資料
        step2_data = wizard_data.get('step2', {})
        initial_data = {'teams_text': "\n".join(step2_data.get('teams', []))}
        form = TeamCreationStep2Form(initial=initial_data)

    return render(request, 'tournaments/wizard_step2.html', {'form': form})

# tournaments/views.py

# ... (檔案上半部所有既有的函式，都維持不變) ...

# 在檔案最下方新增這個函式
@login_required
@user_passes_test(is_superuser, login_url='/admin/')
def tournament_create_step3(request):
    # 從 session 中讀取所有暫存的資料
    wizard_data = request.session.get('wizard_data', {})
    step1_data = wizard_data.get('step1', {})
    step2_data = wizard_data.get('step2', {})

    # 如果 session 中沒有資料，就導回第一步
    if not step1_data or not step2_data:
        return redirect('tournament_create_step1')

    # 如果使用者是按下「確認建立」按鈕
    if request.method == 'POST':
        # --- 開始將資料寫入資料庫 ---

        # 1. 建立 Tournament 物件
        new_tournament = Tournament.objects.create(
            name=step1_data['name'],
            game=step1_data['game'],
            format=step1_data['format'],
            rules=step1_data['rules'],
            start_date=step1_data['start_date'],
            end_date=step1_data['end_date'],
        )

        # 2. 建立或取得 Team 物件，並加入到賽事中
        team_objects = []
        for team_name in step2_data['teams']:
            # get_or_create: 如果隊伍已存在，就直接取得；如果不存在，就建立一個新的
            team, created = Team.objects.get_or_create(name=team_name)
            team_objects.append(team)

        # 將所有隊伍一次性地加入賽事的 participants 欄位
        new_tournament.participants.add(*team_objects)

        # 3. (可選) 如果是分組循環，可以自動建立一個預設分組
        if new_tournament.format == 'round_robin':
            default_group = Group.objects.create(tournament=new_tournament, name="預設分組")
            default_group.teams.add(*team_objects)

        # 4. 清除 session，完成任務
        del request.session['wizard_data']

        # 5. 導向到新建立的賽事詳情頁
        return redirect('tournament_detail', pk=new_tournament.pk)

    # 如果是第一次瀏覽此頁面，就顯示預覽
    context = {
        'step1_data': step1_data,
        'step2_data': step2_data,
    }
    return render(request, 'tournaments/wizard_step3.html', context)

def player_detail(request, pk):
    # 根據網址傳來的 pk，去資料庫找對應的 Player
    player = get_object_or_404(Player.objects.select_related('team'), pk=pk)

    # 從選手身上，反向查詢所有他打過的比賽數據
    # .select_related() 用來優化查詢，一次性抓取相關的比賽和賽事資訊
    stats = player.game_stats.select_related(
        'game__match', 'game__match__tournament', 'game__match__team1', 'game__match__team2'
    ).order_by('-game__match__match_time') # 讓最新的比賽顯示在最上面

    context = {
        'player': player,
        'stats': stats,
    }

    return render(request, 'tournaments/player_detail.html', context)

@login_required
def generate_tournament_schedule(request, pk):
    """自動產生賽事賽程"""
    tournament = get_object_or_404(Tournament, pk=pk)
    
    if request.method == 'POST':
        try:
            if tournament.format == 'round_robin':
                # 檢查是否有分組
                if not tournament.groups.exists():
                    messages.error(request, '請先建立分組才能產生賽程')
                    return redirect('tournament_detail', pk=pk)
                
                # 清理舊的積分表
                from .models import Standing
                Standing.objects.filter(tournament=tournament).delete()
                
                # 為所有分組隊伍建立積分表，按分組名稱排序
                groups = tournament.groups.order_by('name')
                for group in groups:
                    for team in group.teams.all():
                        # 檢查是否已存在，避免重複建立
                        if not Standing.objects.filter(tournament=tournament, team=team, group=group).exists():
                            Standing.objects.create(tournament=tournament, team=team, group=group)
                
                # 產生比賽
                count = generate_round_robin_matches(tournament)
                messages.success(request, f'已成功產生 {count} 場分組循環賽')
                
            elif tournament.format == 'swiss':
                # 確保所有參賽隊伍都有積分紀錄
                from .models import Standing
                existing_teams = set(Standing.objects.filter(tournament=tournament).values_list('team_id', flat=True))
                for team in tournament.participants.all():
                    if team.id not in existing_teams:
                        Standing.objects.create(tournament=tournament, team=team)
                
                count = generate_swiss_round_matches(tournament)
                messages.success(request, f'已成功產生 {count} 場瑞士輪比賽')
                
            elif tournament.format == 'single_elimination':
                # 檢查是否有參賽隊伍
                if not tournament.participants.exists():
                    messages.error(request, '請先添加參賽隊伍才能產生賽程')
                    return redirect('tournament_detail', pk=pk)
                
                count = generate_single_elimination_matches(tournament)
                messages.success(request, f'已成功產生 {count} 場單淘汰賽')
                
            elif tournament.format == 'double_elimination':
                # 檢查是否有參賽隊伍
                if not tournament.participants.exists():
                    messages.error(request, '請先添加參賽隊伍才能產生賽程')
                    return redirect('tournament_detail', pk=pk)
                
                count = generate_double_elimination_matches(tournament)
                messages.success(request, f'已成功產生 {count} 場雙淘汰賽')
                
            else:
                messages.error(request, f'不支援的賽制：{tournament.get_format_display()}')
                
        except Exception as e:
            messages.error(request, f'產生賽程時發生錯誤：{str(e)}')
    
    return redirect('tournament_detail', pk=pk)


# ===== 自動隨機分組功能 =====
@login_required
@user_passes_test(is_superuser, login_url='/admin/')
def auto_random_grouping(request, pk):
    """
    自動隨機分組功能
    根據參賽隊伍數量自動建議分組數，並隨機分配隊伍到各組
    """
    tournament = get_object_or_404(Tournament, id=pk)
    
    if request.method == 'POST':
        # 獲取分組數量
        num_groups = int(request.POST.get('num_groups', 2))
        
        # 清除現有分組
        tournament.groups.all().delete()
        
        # 獲取所有參賽隊伍
        teams = list(tournament.participants.all())
        
        if len(teams) < num_groups:
            messages.error(request, f'參賽隊伍數量({len(teams)})不能少於分組數量({num_groups})')
            return redirect('tournament_detail', pk=pk)
        
        # 隨機打亂隊伍順序
        random.shuffle(teams)
        
        # 創建分組
        groups = []
        for i in range(num_groups):
            group_name = chr(65 + i) + '組'  # A組, B組, C組...
            group = Group.objects.create(
                tournament=tournament,
                name=group_name
            )
            groups.append(group)
        
        # 平均分配隊伍到各組
        for i, team in enumerate(teams):
            group_index = i % num_groups
            groups[group_index].teams.add(team)
        
        # 為每個分組創建 Standing 記錄
        for group in groups:
            for team in group.teams.all():
                Standing.objects.get_or_create(
                    tournament=tournament,
                    team=team,
                    group=group,
                    defaults={
                        'wins': 0,
                        'losses': 0,
                        'draws': 0,
                        'points': 0
                    }
                )
        
        messages.success(request, f'成功創建 {num_groups} 個分組，已隨機分配 {len(teams)} 支隊伍')
        return redirect('tournament_detail', pk=pk)
    
    # GET 請求 - 顯示分組設定頁面
    teams = tournament.participants.all()
    num_teams = len(teams)
    
    # 建議分組數量（每組 3-6 支隊伍為佳）
    suggested_groups = []
    if num_teams >= 6:
        for groups in range(2, min(num_teams // 2 + 1, 8)):  # 最多 8 組
            teams_per_group = num_teams / groups
            if 3 <= teams_per_group <= 6:  # 每組 3-6 支隊伍
                suggested_groups.append({
                    'num_groups': groups,
                    'teams_per_group': f'{math.floor(teams_per_group)}-{math.ceil(teams_per_group)}',
                    'description': f'{groups} 組 (每組約 {teams_per_group:.1f} 支隊伍)'
                })
    
    # 如果沒有合適的建議，至少提供 2 組的選項
    if not suggested_groups:
        suggested_groups.append({
            'num_groups': 2,
            'teams_per_group': f'{num_teams // 2}' if num_teams % 2 == 0 else f'{num_teams // 2}-{num_teams // 2 + 1}',
            'description': f'2 組 (每組約 {num_teams / 2:.1f} 支隊伍)'
        })
    
    context = {
        'tournament': tournament,
        'teams': teams,
        'num_teams': num_teams,
        'suggested_groups': suggested_groups,
        'existing_groups': tournament.groups.all()
    }
    
    return render(request, 'tournaments/auto_grouping.html', context)