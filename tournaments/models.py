from django.db import models
from django.utils import timezone
from django.urls import reverse


class Tournament(models.Model):
    class Format(models.TextChoices):
        SINGLE_ELIMINATION = 'single_elimination', '單敗淘汰'
        DOUBLE_ELIMINATION = 'double_elimination', '雙敗淘汰'
        ROUND_ROBIN = 'round_robin', '分組循環'
        SWISS = 'swiss', '瑞士輪'

    name = models.CharField(max_length=200, verbose_name="賽事名稱")
    game = models.CharField(max_length=100, verbose_name="遊戲名稱")
    start_date = models.DateTimeField(default=timezone.now, verbose_name="報名開始日期")
    end_date = models.DateTimeField(verbose_name="賽事結束日期")
    rules = models.TextField(verbose_name="賽事規章")
    status = models.CharField(
        max_length=10, 
        choices=[('upcoming', '尚未開始'), ('ongoing', '進行中'), ('finished', '已結束')], 
        default='upcoming', 
        verbose_name="賽事狀態"
    )
    participants = models.ManyToManyField('Team', related_name='tournaments', blank=True, verbose_name="參賽隊伍")
    format = models.CharField(
        max_length=20,
        choices=Format.choices,
        default=Format.SINGLE_ELIMINATION,
        verbose_name="賽制"
    )

    def __str__(self):
        return self.name

class Team(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="隊伍名稱")
    school = models.CharField(max_length=200, blank=True, verbose_name="學校名稱")
    logo = models.ImageField(upload_to='team_logos/', null=True, blank=True, verbose_name="隊伍Logo")

    def __str__(self):
        return self.name
    def get_absolute_url(self):
        return reverse('team_detail', kwargs={'pk': self.pk})

PLAYER_ROLES = [
    ('Duelist', '決鬥者'),
    ('Initiator', '先鋒'),
    ('Controller', '煙位'),
    ('Sentinel', '守衛'),
    ('Flex', '自由位'),
]

class Player(models.Model):
    nickname = models.CharField(max_length=100, verbose_name="遊戲內暱稱")
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='players', verbose_name="所屬隊伍")
    avatar = models.ImageField(upload_to='player_avatars/', null=True, blank=True, verbose_name="選手頭像")
    # ADD THIS NEW FIELD
    role = models.CharField(
        max_length=20,
        choices=PLAYER_ROLES,
        default='Flex',
        verbose_name='角色定位'
    )

    def __str__(self):
        return f"{self.nickname} ({self.team.name})"
    def get_absolute_url(self):
        return reverse('player_detail', kwargs={'pk': self.pk})

class Match(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='matches', verbose_name="所屬賽事")
    round_number = models.PositiveIntegerField(verbose_name="比賽輪次")
    map = models.CharField(max_length=100, blank=True, null=True, verbose_name="地圖")
    team1 = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, related_name='matches_as_team1', verbose_name="隊伍一")
    team2 = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, related_name='matches_as_team2', verbose_name="隊伍二")
    team1_score = models.PositiveIntegerField(default=0, verbose_name="隊伍一得分")
    team2_score = models.PositiveIntegerField(default=0, verbose_name="隊伍二得分")
    winner = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='won_matches', verbose_name="勝者")
    match_time = models.DateTimeField(null=True, blank=True, verbose_name="預計比賽時間")
    status = models.CharField(
        max_length=10, 
        choices=[('scheduled', '尚未開始'), ('completed', '已結束')], 
        default='scheduled', 
        verbose_name="比賽狀態"
    )
    is_lower_bracket = models.BooleanField(default=False, verbose_name="是否為敗部賽")

    def __str__(self):
        bracket = " (敗部)" if self.is_lower_bracket else ""
        t1_name = self.team1.name if self.team1 else "待定 (TBD)"
        t2_name = self.team2.name if self.team2 else "待定 (TBD)"
        return f"{self.tournament.name} - R{self.round_number}{bracket}: {t1_name} vs {t2_name}"
    
class Game(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='games', verbose_name="所屬比賽")
    map_number = models.PositiveIntegerField(verbose_name="地圖編號") # e.g., 1, 2, 3
    map_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="地圖名稱") # e.g., "Ascent"
    team1_score = models.PositiveIntegerField(default=0, verbose_name="隊伍一地圖得分") # e.g., 13
    team2_score = models.PositiveIntegerField(default=0, verbose_name="隊伍二地圖得分") # e.g., 5
    winner = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='won_games', verbose_name="地圖勝者")

    class Meta:
        unique_together = ('match', 'map_number') # 一場比賽中，地圖編號是唯一的
        ordering = ['map_number']

    def __str__(self):
        return f"{self.match} - Map {self.map_number}"

class Group(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='groups', verbose_name="所屬賽事")
    name = models.CharField(max_length=100, verbose_name="組別名稱") # 例如: "A組", "B組"
    max_teams = models.PositiveIntegerField(default=8, verbose_name="最大隊伍數")
    teams = models.ManyToManyField(Team, related_name='tournament_groups', verbose_name="組內隊伍")

    def __str__(self):
        return f"{self.tournament.name} - {self.name}"

class Standing(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='standings', verbose_name="所屬賽事")
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='standings', verbose_name="隊伍")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True, related_name='standings', verbose_name="所屬分組")
    wins = models.PositiveIntegerField(default=0, verbose_name="勝場")
    losses = models.PositiveIntegerField(default=0, verbose_name="敗場")
    draws = models.PositiveIntegerField(default=0, verbose_name="平局")
    points = models.IntegerField(default=0, verbose_name="積分")

    class Meta:
        unique_together = ('tournament', 'team')

    def __str__(self):
        return f"{self.tournament.name} - {self.team.name}: {self.points}分"

class PlayerGameStat(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='player_stats', verbose_name="對應小局")
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='game_stats', verbose_name="選手")
    team = models.ForeignKey(Team, on_delete=models.CASCADE, verbose_name="代表隊伍")
    kills = models.PositiveIntegerField(default=0, verbose_name="擊殺")
    deaths = models.PositiveIntegerField(default=0, verbose_name="死亡")
    assists = models.PositiveIntegerField(default=0, verbose_name="助攻")
    first_kills = models.PositiveIntegerField(default=0, verbose_name="首殺")
    acs = models.FloatField(default=0.0, verbose_name="ACS")

    class Meta:
        # unique_together 現在是 game 和 player
        unique_together = ('game', 'player')
        verbose_name = "選手單局數據"
        verbose_name_plural = "選手單局數據"

    def __str__(self):
        return f"{self.game} - {self.player.nickname}: KDA({self.kills}/{self.deaths}/{self.assists})"