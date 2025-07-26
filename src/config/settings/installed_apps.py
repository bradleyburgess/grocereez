DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRDPARTY_APPS = [
    "crispy_forms",
    "crispy_bootstrap5",
]

PROJECT_APPS = [
    "users",
]

INSTALLED_APPS = DJANGO_APPS + THIRDPARTY_APPS + PROJECT_APPS
