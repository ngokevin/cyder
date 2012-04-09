# This is your project's main settings file that can be committed to your
# repo. If you need to override a setting locally, use settings_local.py

import os

from funfactory.settings_base import *

CAS_SERVER_URL = "https://login.oregonstate.edu/cas/login"

CYDNS_BASE_URL = "/cydns"

# os.environ['FORCE_DB']='1'

JINJA_CONFIG = {'autoescape': False}

# NOSE_ARGS = ['-s', '-v', '-d' ]
NOSE_ARGS = [ '-s', '-v', '-d', '--cover-package=cyder', "--with-coverage"  ]

# Bundles is a dictionary of two dictionaries, css and js, which list css files
# and js files that can be bundled together by the minify app.
MINIFY_BUNDLES = {
    'css': {
        'example_css': (
            'css/examples/main.css',
        ),
        'example_mobile_css': (
            'css/examples/mobile.css',
        ),
    },
    'js': {
        'example_js': (
            'js/examples/libs/jquery-1.4.4.min.js',
            'js/examples/libs/jquery.cookie.js',
            'js/examples/init.js',
        ),
    }
}

# Defines the views served for root URLs.
ROOT_URLCONF = 'cyder.urls'

APPEND_SLASH = True

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': os.path.join(os.path.dirname(__file__), 'whoosh_index'),
        },
}


INSTALLED_APPS = list(INSTALLED_APPS) + [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    # Application base, containing global templates.
    #'django.contrib.staticfiles',
    'haystack',
    'cyder.base',
    'cyder.search',
    'cyder.core.cyuser',
    'cyder.core',
    'cyder.core.ctnr',
    'cyder.core.registrations',
    'cyder.core.node',
    'cyder.cybind',
    'cyder.cydns',
    'cyder.cydns.address_record',
    'cyder.cydns.cname',
    'cyder.cydns.domain',
    'cyder.cydns.ip',
    'cyder.cydns.mx',
    'cyder.cydns.nameserver',
    'cyder.cydns.nameserver.nameserver',
    'cyder.cydns.nameserver.reverse_nameserver',
    'cyder.cydns.ptr',
    'cyder.cydns.reverse_domain',
    'cyder.cydns.soa',
    'cyder.cydns.srv',
    'cyder.cydns.txt',
    'cyder.cydhcp',
    'cyder.cydhcp.class_option',
    'cyder.cydhcp.group',
    'cyder.cydhcp.group_option',
    'cyder.cydhcp.pool_option',
    'cyder.cydhcp.range',
    'cyder.cydhcp.subnet',
    'cyder.cydhcp.subnet_option',
    'cyder.maintain2cyder',
]


# Because Jinja2 is the default template loader, add any non-Jinja templated
# apps here:
JINGO_EXCLUDE_APPS = [
    'admin',
]

# Tells the extract script what files to look for L10n in and what function
# handles the extraction. The Tower library expects this.

# # Use this if you have localizable HTML files:
# DOMAIN_METHODS['lhtml'] = [
#    ('**/templates/**.lhtml',
#        'tower.management.commands.extract.extract_tower_template'),
# ]

# # Use this if you have localizable HTML files:
# DOMAIN_METHODS['javascript'] = [
#    # Make sure that this won't pull in strings from external libraries you
#    # may use.
#    ('media/js/**.js', 'javascript'),
# ]
LOGGING = dict(loggers=dict(playdoh = {'level': logging.DEBUG}))

AUTH_PROFILE_MODULE = 'cyuser.UserProfile'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'django_cas.backends.CASBackend',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'cyder_db',
        'TEST_NAME':'cyder_db_test',
        },
}

MIDDLEWARE_CLASSES = (
    #'cyder.middleware.authentication.AuthenticationMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django_cas.middleware.CASMiddleware',

)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    #'django_cas.backends.CASBackend',
    'django_cas.middleware.CASMiddleware',
    'cyder.middleware.authentication.AuthenticationMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
)

TEMPLATE_LOADERS = (
    'jingo.Loader',
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

