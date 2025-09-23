from django import forms
from .models import Tournament, Team

class TournamentCreationStep1Form(forms.ModelForm):
    """
    賽事建立精靈 - 步驟一: 基本資訊
    """
    class Meta:
        model = Tournament
        fields = ['name', 'game', 'format', 'rules', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class TeamCreationStep2Form(forms.Form):
    """
    賽事建立精靈 - 步驟二: 新增參賽隊伍
    """
    teams_text = forms.CharField(
        widget=forms.Textarea,
        label="參賽隊伍名單",
        help_text="請每行輸入一個隊伍名稱。例如：\n隊伍A\n隊伍B\n隊伍C"
    )