# esports_site/urls.py

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.views.static import serve

urlpatterns = [
    # Admin 路由
    path('admin/', admin.site.urls),
    
    # 監控儀表板路由
    path('monitoring/', include('monitoring.urls')),
    
    # 主要應用路由
    path('', include('tournaments.urls')),

    # API 路由
    path('api/', include('tournaments.api_urls')),
    
    # 大寫 API 重定向到小寫 (可選)
    path('API/', RedirectView.as_view(url='/api/', permanent=True)),
    path('API', RedirectView.as_view(url='/api/', permanent=True)),
]

# ===== Media 文件處理 - 強制使用 Django 服務所有環境 =====
# 使用 Django 的內建 serve 視圖來服務 media 文件，解決 Render 生產環境問題
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
]

# 額外的靜態文件配置（備用）
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)