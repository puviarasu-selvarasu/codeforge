import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'jSuBh_4bB_AE9VkY5PdQggDEHYgUfKCM3KYMM1OtAVtBeR4GSTgXMxJKOtkDKd3m5Rs'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Our apps
    'apps.core',
    'apps.chat',
    'apps.knowledge',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --------------------------------------------------------
# CodeForge Custom Settings
# --------------------------------------------------------

# Root directories (will be created automatically)
KNOWLEDGE_ROOT = BASE_DIR / 'knowledge'
LANCEDB_ROOT = BASE_DIR / 'lancedb'

# Resource thresholds (in bytes)
MIN_FREE_RAM_BYTES = 1.5 * 1024 ** 3  # 1.5 GB

# ============================================================
# LLM Model Settings (Phase 4.6)
# ============================================================
LLM_15B_MODEL_PATH = BASE_DIR / 'models' / 'qwen2.5-coder-1.5b-instruct-q4_k_m.gguf'
LLM_7B_MODEL_PATH = BASE_DIR / 'models' / 'qwen2.5-coder-7b-instruct-q5_k_m.gguf'

# Default model (used in Dashboard and initial Studio load)
DEFAULT_LLM_MODEL = '1.5B'   # options: '1.5B' or '7B'

LLM_7B_MAX_TOKENS = 3072
LLM_15B_MAX_TOKENS = 1024

# Inference settings (shared by both models)
LLM_N_CTX = 4096
LLM_N_BATCH = 256
LLM_N_THREADS = 4

# Embedding model
EMBEDDING_MODEL_NAME = 'BAAI/bge-small-en-v1.5'

# Create the directories if they don't exist
os.makedirs(KNOWLEDGE_ROOT, exist_ok=True)
os.makedirs(LANCEDB_ROOT, exist_ok=True)
os.makedirs(BASE_DIR / 'models', exist_ok=True)