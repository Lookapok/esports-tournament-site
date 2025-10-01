# esports_site/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

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

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)