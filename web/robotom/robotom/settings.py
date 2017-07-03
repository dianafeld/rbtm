# Django settings for robotom project.

from urlparse import urljoin
import os

DEBUG = False
TEMPLATE_DEBUG = DEBUG
REQUEST_DEBUG = False

TIMEOUT_DEFAULT = 120  # timeout in secs

STORAGE_HOST = 'http://storage_server_1:5006/'

STORAGE_FRAMES_PNG = urljoin(STORAGE_HOST, '/storage/experiments/{exp_id}/frames/{frame_id}/png')
STORAGE_FRAMES_INFO_HOST = urljoin(STORAGE_HOST, '/storage/frames_info/get')
STORAGE_FRAMES_HOST = urljoin(STORAGE_HOST, '/storage/frames/get')
STORAGE_EXPERIMENTS_GET_HOST = urljoin(STORAGE_HOST, '/storage/experiments/get')
STORAGE_CREATE_USER_HOST = urljoin(STORAGE_HOST, '/storage/users/get')
STORAGE_ALT_USER_HOST = urljoin(STORAGE_HOST, '/storage/users/update')
STORAGE_EXPERIMENTS_HOST = urljoin(STORAGE_HOST, '/storage/experiments')
STORAGE_HDF5_FILE = '/storage/experiments/{exp_id}.h5'
STORAGE_RECONSTRUCTION = urljoin(STORAGE_HOST, '/storage/experiments/{exp_id}/3d/{rarefaction}/{level1}/{level2}')

EXPERIMENT_HOST = 'http://10.0.3.104:5001/'
# address templates, where {} is a placeholder for tomograph number
EXPERIMENT_SOURCE_POWER_ON = urljoin(EXPERIMENT_HOST, '/tomograph/{}/source/power-on')
EXPERIMENT_SOURCE_POWER_OFF = urljoin(EXPERIMENT_HOST, '/tomograph/{}/source/power-off')

EXPERIMENT_MOTOR_SET_HORIZ = urljoin(EXPERIMENT_HOST, '/tomograph/{}/motor/set-horizontal-position')
EXPERIMENT_MOTOR_SET_VERT = urljoin(EXPERIMENT_HOST, '/tomograph/{}/motor/set-vertical-position')
EXPERIMENT_MOTOR_SET_ANGLE = urljoin(EXPERIMENT_HOST, '/tomograph/{}/motor/set-angle-position')
EXPERIMENT_MOTOR_RESET_ANGLE = urljoin(EXPERIMENT_HOST, '/tomograph/{}/motor/reset-angle-position')
EXPERIMENT_SHUTTER_OPEN = urljoin(EXPERIMENT_HOST, '/tomograph/{}/shutter/open/0')
EXPERIMENT_SHUTTER_CLOSE = urljoin(EXPERIMENT_HOST, '/tomograph/{}/shutter/close/0')
EXPERIMENT_SOURCE_SET_VOLT = urljoin(EXPERIMENT_HOST, '/tomograph/{}/source/set-voltage')
EXPERIMENT_SOURCE_SET_CURR = urljoin(EXPERIMENT_HOST, '/tomograph/{}/source/set-current')
EXPERIMENT_DETECTOR_GET_FRAME = urljoin(EXPERIMENT_HOST, '/tomograph/{}/detector/get-frame')

EXPERIMENT_START = urljoin(EXPERIMENT_HOST, '/tomograph/{}/experiment/start')
EXPERIMENT_STOP = urljoin(EXPERIMENT_HOST, '/tomograph/{}/experiment/stop')

EXPERIMENT_MOTOR_GET_HORIZ = urljoin(EXPERIMENT_HOST, '/tomograph/{}/motor/get-horizontal-position')
EXPERIMENT_MOTOR_GET_VERT = urljoin(EXPERIMENT_HOST, '/tomograph/{}/motor/get-vertical-position')
EXPERIMENT_MOTOR_GET_ANGLE = urljoin(EXPERIMENT_HOST, '/tomograph/{}/motor/get-angle-position')
EXPERIMENT_SHUTTER_GET_STATUS = urljoin(EXPERIMENT_HOST, '/tomograph/{}/shutter/state')
EXPERIMENT_SOURCE_GET_VOLT = urljoin(EXPERIMENT_HOST, '/tomograph/{}/source/get-voltage')
EXPERIMENT_SOURCE_GET_CURR = urljoin(EXPERIMENT_HOST, '/tomograph/{}/source/get-current')

EXPERIMENT_GET_STATE = urljoin(EXPERIMENT_HOST, '/tomograph/{}/state')

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..')

ADMINS = (
    ('Robotom Admins', 'robotomproject@gmail.com'),
)

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.CryptPasswordHasher',
)

DEFAULT_FROM_EMAIL = 'robotomproject@gmail.com'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'robotom_users',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '',
    },
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['109.234.38.83', 'xtomo.ru', 'www.xtomo.ru']

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Moscow'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'ru-ru'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = False

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = (os.path.join(BASE_DIR, 'media/'))
RECONSTRUCTION_ROOT = (os.path.join(BASE_DIR, 'media/reconstructions/'))

MEDIA_URL = '/media/'

SENDFILE_ROOT = MEDIA_ROOT

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
)

SENDFILE_BACKEND = 'sendfile.backends.development'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'main/static'), )

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'vn)82k3mmx_41^em04jxb-ri=asbcs(=(^=r1h89d%gk4d7*v='

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    # 'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'robotom.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'robotom.wsgi.application'

TEST_RUNNER = 'xmlrunner.extra.djangotestrunner.XMLTestRunner'
TEST_OUTPUT_DIR = 'robotom/test-reports/'

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'registration',
    'bootstrap3',
    'rest_framework',

    'main',
    'experiment',
    'storage',
)

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'


def skip_suspicious_operations(record):
    if record.name == 'django.security.DisallowedHost':
        return False
    return True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'skip_suspicious_operations': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': skip_suspicious_operations,
        }
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false', 'skip_suspicious_operations'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'write_to_storage_log': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/storage.log'),
            'formatter': 'verbose',
        },
        'write_to_experiment_log': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/experiment.log'),
            'formatter': 'verbose',
        },
        'write_to_main_log': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/main.log'),
            'formatter': 'verbose',
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.security': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'storage_logger': {
            'handlers': ['write_to_storage_log'],
            'level': 'DEBUG',
        },
        'experiment_logger': {
            'handlers': ['write_to_experiment_log'],
            'level': 'DEBUG',
        },
        'main_logger': {
            'handlers': ['write_to_main_log'],
            'level': 'DEBUG',
        },
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

try:
    from robotom.local_settings import *
except BaseException:
    pass
