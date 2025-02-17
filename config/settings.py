"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""
import os

import mongoengine
from dotenv import load_dotenv
from pathlib import Path
from neomodel import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/
# Load environment variables
load_dotenv()

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-$d(7)8kcd!j7qk+ifn(0h(#0z!$3$_inr#34x@0+*5_s^-^4-('

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG') == 'True'

ALLOWED_HOSTS = ["*"]

CSRF_TRUSTED_ORIGINS = ["http://127.0.0.1:8000", ]
CORS_ORIGIN_ALLOW_ALL = True

# Connect to Neo4j database
neo4j_username = os.environ.get('NEO4J_USERNAME')
neo4j_password = os.environ.get('NEO4J_PASSWORD')
neo4j_host = os.environ.get('NEO4J_HOST')
neo4j_port = os.environ.get('NEO4J_PORT')

# config.DATABASE_URL = f'bolt://{neo4j_username}:{neo4j_password}@{neo4j_host}:{neo4j_port}'
try:
    if DEBUG:
        config.DATABASE_URL = f'bolt://{neo4j_username}:{neo4j_password}@{neo4j_host}:{neo4j_port}'
    else:
        config.DATABASE_URL = f'bolt+s://{neo4j_username}:{neo4j_password}@{neo4j_host}:{neo4j_port}'
except Exception as e:
    raise ValueError(f"Error connecting to Neo4j database: {e}")

mongo_db_name = os.environ.get('MONGO_DB_NAME')
mongo_db_username = os.environ.get('MONGO_DB_USERNAME')
mongo_db_password = os.environ.get('MONGO_DB_PASSWORD')
mongo_host = os.environ.get("MONGO_DB_HOST")
mongo_port = os.environ.get("MONGO_DB_PORT")

mongo_uri = f'mongodb://{mongo_db_username}:{mongo_db_password}@{mongo_host}:{mongo_port}/{mongo_db_name}?authSource=admin'
# print(mongo_uri)
mongoengine.connect(host=mongo_uri)
# mongoengine.connect(
#     db='dtl'
# )

# bolt+s://<username>:<password>@<host>:<port>
# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_mongoengine',
    'django_neomodel',
    'corsheaders',
    'drf_spectacular',
    'apps',
    'apps.search_engine',
    'apps.scopus_integration',
    'apps.dashboards',
    'apps.authentication'
]

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}
log_dir = Path(BASE_DIR) / 'centinela_logs'
if not log_dir.exists():
    log_dir.mkdir(parents=True)

# LOGGING = {
#     "version": 1,
#     "disable_existing_loggers": False,
#     "handlers": {
#         "file": {
#             "level": "INFO",
#             "class": "logging.handlers.TimedRotatingFileHandler",
#             "filename": os.path.join(log_dir, "info.log"),
#             "when": "midnight",
#             "backupCount": 7,
#             "formatter": "verbose",
#             "encoding": "utf-8",
#             "delay": True
#         },
#     },
#     "formatters": {
#         "verbose": {
#             "format": "{asctime} {levelname} {message}",
#             "style": "{",
#         },
#     },
#     "loggers": {
#         "django": {
#             "handlers": ["file"],
#             "level": "DEBUG",
#             "propagate": True,
#         },
#     },
# }

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{asctime} {levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": os.path.join(log_dir, "info.log"),
            "when": "midnight",
            "backupCount": 7,
            "formatter": "verbose",
            "encoding": "utf-8",
            "delay": True
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file", "console"],  # Agregamos console aquí
            "level": "DEBUG",
            "propagate": True,
        },
        # Agregamos un logger específico para tus apps
        "apps": {
            "handlers": ["file", "console"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Search Engine API',
    'DESCRIPTION': 'This project contains the API for the Search Engine project and Scoopus Integration project.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
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
        'DIRS': [BASE_DIR / 'templates']
        ,
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
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    },
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# """
# Django settings for config project.
#
# Generated by 'django-admin startproject' using Django 5.0.6.
#
# For more information on this file, see
# https://docs.djangoproject.com/en/5.0/topics/settings/
#
# For the full list of settings and their values, see
# https://docs.djangoproject.com/en/5.0/ref/settings/
# """
# import os
#
# import mongoengine
# from dotenv import load_dotenv
# from pathlib import Path
# from neomodel import config
#
# # Build paths inside the project like this: BASE_DIR / 'subdir'.
# BASE_DIR = Path(__file__).resolve().parent.parent
#
# # Quick-start development settings - unsuitable for production
# # See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/
# # Load environment variables
# load_dotenv()
#
# # SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = 'django-insecure-$d(7)8kcd!j7qk+ifn(0h(#0z!$3$_inr#34x@0+*5_s^-^4-('
#
# # SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = True
#
# ALLOWED_HOSTS = []
#
# # Connect to Neo4j database
# neo4j_username = 'neo4j'
# neo4j_password = 'narias98'
# neo4j_host = 'localhost'
# neo4j_port = '7687'
#
# config.DATABASE_URL = f'bolt://{neo4j_username}:{neo4j_password}@{neo4j_host}:{neo4j_port}'
# # bolt+s://<username>:<password>@<host>:<port>
# mongoengine.connect(db="datalake")
#
# # Application definition
# INSTALLED_APPS = [
#     'django.contrib.admin',
#     'django.contrib.auth',
#     'django.contrib.contenttypes',
#     'django.contrib.sessions',
#     'django.contrib.messages',
#     'django.contrib.staticfiles',
#     'rest_framework',
#     'django_neomodel',
#     'drf_spectacular',
#     'apps',
#     'apps.search_engine',
#     'apps.scopus_integration',
#     'apps.dashboards',
#     'corsheaders'
# ]
#
# REST_FRAMEWORK = {
#     'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
#     'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
#     'PAGE_SIZE': 10
# }
#
# SPECTACULAR_SETTINGS = {
#     'TITLE': 'Search Engine API',
#     'DESCRIPTION': 'This project contains the API for the Search Engine project and Scoopus Integration project.',
#     'VERSION': '1.0.0',
#     'SERVE_INCLUDE_SCHEMA': False,
# }
#
# MIDDLEWARE = [
#     'corsheaders.middleware.CorsMiddleware',
#     'django.middleware.security.SecurityMiddleware',
#     'django.contrib.sessions.middleware.SessionMiddleware',
#     'django.middleware.common.CommonMiddleware',
#     'django.middleware.csrf.CsrfViewMiddleware',
#     'django.contrib.auth.middleware.AuthenticationMiddleware',
#     'django.contrib.messages.middleware.MessageMiddleware',
#     'django.middleware.clickjacking.XFrameOptionsMiddleware',
# ]
#
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:4200",
#     # otros orígenes permitidos
# ]
#
# ROOT_URLCONF = 'config.urls'
#
# TEMPLATES = [
#     {
#         'BACKEND': 'django.template.backends.django.DjangoTemplates',
#         'DIRS': [BASE_DIR / 'templates']
#         ,
#         'APP_DIRS': True,
#         'OPTIONS': {
#             'context_processors': [
#                 'django.template.context_processors.debug',
#                 'django.template.context_processors.request',
#                 'django.contrib.auth.context_processors.auth',
#                 'django.contrib.messages.context_processors.messages',
#             ],
#         },
#     },
# ]
#
# WSGI_APPLICATION = 'config.wsgi.application'
#
# # Database
# # https://docs.djangoproject.com/en/5.0/ref/settings/#databases
#
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     },
# }
#
# # Password validation
# # https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators
#
# AUTH_PASSWORD_VALIDATORS = [
#     {
#         'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
#     },
# ]
#
# # Internationalization
# # https://docs.djangoproject.com/en/5.0/topics/i18n/
#
# LANGUAGE_CODE = 'en-us'
#
# TIME_ZONE = 'UTC'
#
# USE_I18N = True
#
# USE_TZ = True
#
# # Static files (CSS, JavaScript, Images)
# # https://docs.djangoproject.com/en/5.0/howto/static-files/
#
# STATIC_URL = 'static/'
#
# # Default primary key field type
# # https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field
#
# DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
