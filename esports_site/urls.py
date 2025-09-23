# esports_site/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # 這一行負責處理給使用者看的所有網頁
    path('', include('tournaments.urls')),

    # --- 新增下面這一行，專門處理 API ---
    path('api/', include('tournaments.api_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)