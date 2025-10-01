from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q
from collections import defaultdict
from .models import Tournament, Match, Team, Player, PlayerGameStat, Group
from .forms import TournamentCreationStep1Form, TeamCreationStep2Form
from .tables import StatsTable
from django.shortcuts import render
from django.contrib import messages
from .logic import generate_round_robin_matches, generate_swiss_round_matches, generate_single_elimination_matches, generate_double_elimination_matches


# tournaments/views.py

def tournament_list(request):
    # 優化：預先抓取每場賽事的主圖，避免在模板中產生額外查詢
    tournaments = Tournament.objects.all().order_by('-start_date')

    # 優化：預先抓取比賽關聯的賽事、隊伍資訊
    upcoming_matches = Match.objects.select_related(
        'tournament', 'team1', 'team2'
    ).filter(
        status='scheduled',
        match_time__gte=timezone.now()
    ).order_by('match_time')[:5]

    context = {
        'tournaments': tournaments,
        'upcoming_matches': upcoming_matches,
    }
    # 確認是渲染到 tournament_list.html
    return render(request, 'tournaments/tournament_list.html', context)

def tournament_detail(request, pk):
    tournament = get_object_or_404(
        Tournament.objects.prefetch_related(
            'participants', 
            'matches__team1', 'matches__team2', 'matches__winner',
            'groups__teams', 'standings__team'
        ), 
        pk=pk
    )
    context = {'tournament': tournament}
    if tournament.format == 'round_robin':
        context['groups'] = tournament.groups.all()
    elif tournament.format == 'swiss':
        context['standings'] = tournament.standings.all().order_by('-points', '-wins')
        matches = tournament.matches.all()
        rounds = defaultdict(list)
        for match in matches:
            rounds[match.round_number].append(match)
        context['rounds'] = dict(rounds)
    else: # Elimination
        matches = tournament.matches.all()
        rounds = defaultdict(list)
        for match in matches:
            rounds[match.round_number].append(match)
        context['rounds'] = dict(rounds)
    return render(request, 'tournaments/tournament_detail.html', context)

def team_list(request):
    teams = Team.objects.prefetch_related('players').all().order_by('name')
    context = {'teams': teams}
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
def dashboard(request):
    return render(request, 'registration/dashboard.html')

def custom_logout(request):
    logout(request)
    return redirect('tournament_list')

# tournaments/views.py

@login_required
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
    stats = player.match_stats.select_related(
        'match', 'match__tournament', 'match__team1', 'match__team2'
    ).order_by('-match__match_time') # 讓最新的比賽顯示在最上面

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
                
                # 為所有分組隊伍建立積分表
                groups = tournament.groups.all()
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