# tournaments/apps.py

from django.apps import AppConfig

class TournamentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tournaments'

    # 新增下面這個 ready 方法
    def ready(self):
        # 這裡是 Django 建議的、用來引入 signals 的標準做法
        import tournaments.signals