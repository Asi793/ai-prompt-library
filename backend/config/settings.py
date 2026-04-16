import os
from pathlib import Path
from urllib.parse import urlparse

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key')

DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = os.environ.get(
    'ALLOWED_HOSTS',
    'ai-prompt-library-1-wr6z.onrender.com,localhost'
).split(',')

CORS_ALLOWED_ORIGINS = [
    'https://ai-prompt-library-omega.vercel.app',
    'http://localhost:4200'
]

REDIS_URL = os.environ.get(
    'REDIS_URL',
    'redis://default:mxtgzJXLjbjsPHHCymMCrxConKclnybV@nozomi.proxy.rlwy.net:22038'
)
parsed_redis_url = urlparse(REDIS_URL)
REDIS_HOST = parsed_redis_url.hostname or os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(parsed_redis_url.port or os.environ.get('REDIS_PORT', '6379'))
REDIS_PASSWORD = parsed_redis_url.password or os.environ.get('REDIS_PASSWORD', '')

DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql://postgres:VikkBuNCdRGnedLYCOnHZbktNdjJGwvv@nozomi.proxy.rlwy.net:47837/railway'
)
parsed_url = urlparse(DATABASE_URL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql' if parsed_url.scheme in ('postgres', 'postgresql') else 'django.db.backends.postgresql',
        'NAME': parsed_url.path.lstrip('/'),
        'USER': parsed_url.username,
        'PASSWORD': parsed_url.password,
        'HOST': parsed_url.hostname,
        'PORT': parsed_url.port or '',
    }
}

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'prompts.apps.PromptsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
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
        'DIRS': [],
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

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')