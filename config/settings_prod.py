from .settings import *
from .prod_secrets import *

ALLOWED_HOSTS = ['petal.x.dam.io']

EMAIL_HOST = 'mail.gandi.net'
EMAIL_HOST_USER = 'petals@dam.io'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'petals@dam.io'
SERVER_EMAIL = 'damien@dam.io'