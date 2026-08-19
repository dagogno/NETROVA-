import os
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='changez-moi-en-production-utilisez-une-vraie-cle')
DEBUG = config('DEBUG', default=True, cast=bool)

# Hosts de base depuis .env
_base_hosts = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

# Ajout automatique de ngrok et domaines courants
ALLOWED_HOSTS = _base_hosts + [
    '*.ngrok.io',
    '*.ngrok-free.app',
    '*.ngrok-stable.app',
    '127.0.0.1',
    'localhost',
]

# Pour ajouter votre domaine ou IP de production, mettez dans .env :
# ALLOWED_HOSTS=localhost,127.0.0.1,mondomaine.com,12.34.56.78

INSTALLED_APPS = [
    'dashboard.apps.DashboardConfig',  # Doit être AVANT django.contrib.admin pour surcharger les templates admin
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'membres',
    'produits',
    'commandes',
    'reseau',
    'partenaires',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'netrova.urls'

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
                'dashboard.context_processors.admin_dashboard_stats',
            ],
        },
    },
]

WSGI_APPLICATION = 'netrova.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Pour la production, décommentez et configurez PostgreSQL :
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': config('DB_NAME'),
#         'USER': config('DB_USER'),
#         'PASSWORD': config('DB_PASSWORD'),
#         'HOST': config('DB_HOST', default='localhost'),
#         'PORT': config('DB_PORT', default='5432'),
#     }
# }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Lome'
USE_I18N = True
USE_TZ = True

# Origines de confiance pour CSRF (ngrok, production)
CSRF_TRUSTED_ORIGINS = [
    'http://localhost',
    'http://127.0.0.1',
    'https://*.ngrok.io',
    'https://*.ngrok-free.app',
    'https://*.ngrok-stable.app',
]
_extra_origin = config('CSRF_TRUSTED_ORIGIN', default='')
if _extra_origin:
    CSRF_TRUSTED_ORIGINS.append(_extra_origin)

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/membres/connexion/'
LOGIN_REDIRECT_URL = '/membres/tableau-de-bord/'
LOGOUT_REDIRECT_URL = '/'

# Numéro WhatsApp NETROVA
NETROVA_WHATSAPP = config('NETROVA_WHATSAPP', default='22890491287')
NETROVA_ZONE = 'Baguida – Lomé et environs'

# Taux de commission
TAUX_COMMISSION_BASE = 0.02        # 2% pour équipe < 10
TAUX_COMMISSION_SENIOR = 0.03      # 3% pour équipe >= 10
SEUIL_COMMISSION_SENIOR = 10       # filleuls directs pour passer à 3%

# Pénalité de retard
TAUX_PENALITE_JOUR = 0.01          # 1% par jour

# Délai de règlement du solde (jours)
DELAI_SOLDE_JOURS = 30
