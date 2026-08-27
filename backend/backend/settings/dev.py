from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-x-0j0$4=9p4u#u9(f44@b^p1poh8#s6fq9u$+y+8@=30u32)%m"

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

CORS_ALLOWED_ORIGINS = ["http://localhost:5173"]


try:
    from .local import *
except ImportError:
    pass
