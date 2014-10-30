from django.conf import settings

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Tan Long', 'tanlong@staff.sina.com.cn'),
)

MANAGERS = ADMINS

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.4/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['*']

# Database config
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/etc/samba/db/django.db',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

# Absolute path to database SMB Samba
SMB_DB = getattr(settings, "SMB_DB", "/etc/samba/db/smbpasswd")

# Password history size. Major to zero
HISTORY_SIZE = getattr(settings, "HISTORY_SIZE", 10)

# Password that are excluded in the register of used passwords
DEFAULT_PASSWD = getattr(settings, "DEFAULT_PASSWD", "12345678910")
