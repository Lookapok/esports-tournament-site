"""
Django settings for esports_site project - 精簡優化版
"""

from pathlib import Path
from decouple import config

# 基本目錄設定
BASE_DIR = Path(__file__).resolve().parent.parent

# 安全設定
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)

# 允許的主機
ALLOWED_HOSTS = [
    '127.0.0.1', 
    'localhost',
    'winnertakesall-tw.onrender.com',
    '.onrender.com',
]

# 生產環境檢測
IS_RENDER = config('RENDER', default=False, cast=bool)

# 生產環境安全設定
if IS_RENDER:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    CSRF_TRUSTED_ORIGINS = [
        'https://winnertakesall-tw.onrender.com',
        'https://*.onrender.com',
    ]

# 應用程式
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework.authtoken',
    'django_tables2',
]

LOCAL_APPS = [
    'tournaments',
    'monitoring',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# 中介軟體
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'monitoring.middleware.APIMonitoringMiddleware',
    'monitoring.middleware.BusinessLogicMiddleware',
]

ROOT_URLCONF = 'esports_site.urls'

# 模板設定
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'esports_site.wsgi.application'

# 資料庫設定
import dj_database_url

DATABASE_URL = config('DATABASE_URL', default='')

# 動態檢測可用的 PostgreSQL 驅動
def get_postgresql_engine():
    try:
        import psycopg2
        return 'django.db.backends.postgresql_psycopg2'
    except ImportError:
        try:
            import psycopg
            return 'django.db.backends.postgresql'
        except ImportError:
            raise Exception("Neither psycopg2 nor psycopg is installed")

if DATABASE_URL:
    # 生產環境：使用 Supabase PostgreSQL
    try:
        DATABASES = {
            'default': dj_database_url.parse(
                DATABASE_URL, 
                conn_max_age=600, 
                conn_health_checks=True
            )
        }
        # 動態設定引擎
        try:
            DATABASES['default']['ENGINE'] = get_postgresql_engine()
        except Exception:
            DATABASES['default']['ENGINE'] = 'django.db.backends.postgresql'
            
        DATABASES['default']['OPTIONS'] = {
            'options': '-c default_transaction_isolation=read_committed'
        }
    except Exception as e:
        print(f"❌ 資料庫配置錯誤: {e}")
        # 緊急回退到 SQLite
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }
else:
    # 本地開發：SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# 密碼驗證
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# 國際化
LANGUAGE_CODE = 'zh-hant'
TIME_ZONE = 'Asia/Taipei'
USE_I18N = True
USE_TZ = True

# 靜態檔案
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []

# 媒體檔案
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# WhiteNoise 靜態檔案配置
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# 預設主鍵類型
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 快取設定
if IS_RENDER:
    # 生產環境：嘗試使用 Redis，失敗則使用內存快取
    try:
        import django_redis
        CACHES = {
            'default': {
                'BACKEND': 'django_redis.cache.RedisCache',
                'LOCATION': config('REDIS_URL', default='redis://127.0.0.1:6379/1'),
                'OPTIONS': {
                    'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                }
            }
        }
    except ImportError:
        # Redis 不可用時使用內存快取
        CACHES = {
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            }
        }
else:
    # 本地開發使用內存快取
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }

# REST Framework 設定
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# 日誌設定
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'django.log',
            'maxBytes': 1024*1024*5,  # 5MB
            'backupCount': 3,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'] if DEBUG else ['file'],
            'level': 'INFO',
            'propagate': False,
        },
        'tournaments': {
            'handlers': ['console', 'file'] if DEBUG else ['file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Debug 模式特殊設定
if DEBUG:
    try:
        print("💻 使用本地記憶體快取")
    except UnicodeEncodeError:
        print("Using local memory cache")
    LOGGING['handlers']['console']['level'] = 'DEBUG'
    for logger in LOGGING['loggers'].values():
        logger['level'] = 'DEBUG'

# 檔案上傳設定
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB
FILE_UPLOAD_MAX_MEMORY_SIZE = MAX_UPLOAD_SIZE
DATA_UPLOAD_MAX_MEMORY_SIZE = MAX_UPLOAD_SIZE
