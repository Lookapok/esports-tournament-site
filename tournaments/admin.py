# tournaments/admin.py

from django.contrib import admin, messages
from .models import Tournament, Team, Player, Match, Group, Standing, PlayerMatchStat
from .logic import generate_round_robin_matches, generate_swiss_round_matches

class PlayerMatchStatInline(admin.TabularInline):
    model = PlayerMatchStat
    extra = 10 
    autocomplete_fields = ['player', 'team'] 

class MatchAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'tournament', 'status')
    list_filter = ('tournament', 'status')
    inlines = [PlayerMatchStatInline]

class GroupInline(admin.TabularInline):
    model = Group.teams.through
    verbose_name = "分組內的隊伍"
    verbose_name_plural = "分組內的隊伍"
    extra = 1

class GroupAdmin(admin.ModelAdmin):
    inlines = [GroupInline]
    list_display = ('name', 'tournament')

@admin.action(description='為選定的賽事自動產生賽程')
def generate_matches_action(modeladmin, request, queryset):
    for tournament in queryset:
        if tournament.format == 'round_robin':
            Standing.objects.filter(tournament=tournament).delete()
            for team in tournament.participants.all():
                Standing.objects.create(tournament=tournament, team=team)
            count = generate_round_robin_matches(tournament)
            modeladmin.message_user(request, f"已為循環賽 '{tournament.name}' 產生了 {count} 場比賽。", messages.SUCCESS)
        elif tournament.format == 'swiss':
            if not Standing.objects.filter(tournament=tournament).exists():
                for team in tournament.participants.all():
                    Standing.objects.create(tournament=tournament, team=team)
            count = generate_swiss_round_matches(tournament)
            modeladmin.message_user(request, f"已為瑞士輪 '{tournament.name}' 產生了 {count} 場新比賽。", messages.SUCCESS)
        else:
            modeladmin.message_user(request, f"賽事 '{tournament.name}' 的賽制 ({tournament.get_format_display()}) 不支援自動產生賽程。", messages.WARNING)

class TournamentAdmin(admin.ModelAdmin):
    list_display = ('name', 'format', 'status')
    list_filter = ('format', 'status')
    actions = [generate_matches_action]

class TeamAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class PlayerAdmin(admin.ModelAdmin):
    list_display = ('nickname', 'team', 'role') 
    list_filter = ('role', 'team') 
    search_fields = ('nickname',)
    autocomplete_fields = ['team'] 

admin.site.register(Tournament, TournamentAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Match, MatchAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Standing)
admin.site.register(PlayerMatchStat)