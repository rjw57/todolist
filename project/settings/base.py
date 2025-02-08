import os
import sys

import externalsettings
import structlog

# By default, make use of connection pooling for the default database and use the Postgres engine.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "CONN_MAX_AGE": 60,  # seconds
    },
}

# If the EXTRA_SETTINGS_URLS environment variable is set, it is a comma-separated list of URLs from
# which to fetch additional settings as YAML-formatted documents. The documents should be
# dictionaries and top-level keys are imported into this module's global values.
_external_setting_urls = []
_external_setting_urls_list = os.environ.get("EXTRA_SETTINGS_URLS", "").strip()
if _external_setting_urls_list != "":
    _external_setting_urls.extend(_external_setting_urls_list.split(","))

externalsettings.load_external_settings(
    globals(),
    urls=_external_setting_urls,
    required_settings=[
        "SECRET_KEY",
        "DATABASES",
        "SOCIAL_AUTH_GOOGLE_OAUTH2_KEY",
        "SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET",
    ],
    optional_settings=[
        "EMAIL_HOST",
        "EMAIL_HOST_PASSWORD",
        "EMAIL_HOST_USER",
        "EMAIL_PORT",
    ],
)

#: Base directory containing the project. Build paths inside the project via
#: ``os.path.join(BASE_DIR, ...)``.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#: SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

#: By default, all hosts are allowed.
ALLOWED_HOSTS = ["*"]

#: Installed applications
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",  # use whitenoise even in development
    "django.contrib.staticfiles",
    "social_django",
    "todolist",
    "ui",
]

#: Installed middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_structlog.middlewares.RequestMiddleware",
]
#: Login configuration
SOCIAL_AUTH_URL_NAMESPACE = "social"
SOCIAL_AUTH_JSONFIELD_ENABLED = True

SOCIAL_AUTH_GOOGLE_OAUTH2_AUTH_EXTRA_ARGUMENTS = {"hd": "cam.ac.uk"}
SOCIAL_AUTH_GOOGLE_OAUTH2_WHITELISTED_DOMAINS = ["cam.ac.uk"]
SOCIAL_AUTH_GOOGLE_OAUTH2_WHITELISTED_HOSTED_DOMAINS = ["cam.ac.uk"]

SOCIAL_AUTH_PIPELINE = (
    "social_core.pipeline.social_auth.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "social_core.pipeline.social_auth.auth_allowed",
    "project.pipelines.enforce_hosted_domain",
    "social_core.pipeline.social_auth.social_user",
    "social_core.pipeline.user.get_username",
    "social_core.pipeline.user.create_user",
    "social_core.pipeline.social_auth.associate_user",
    "social_core.pipeline.social_auth.load_extra_data",
    "social_core.pipeline.user.user_details",
)

LOGIN_URL = "/accounts/login/google-oauth2/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# Serve the frontend files from the application root.
FRONTEND_APP_BUILD_DIR = os.environ.get(
    "DJANGO_FRONTEND_APP_BUILD_DIR",
    os.path.abspath(os.path.join(BASE_DIR, "ui", "frontend", "build")),
)

# If the build directory for the frontend actually exists, serve files for the root of the
# application from it. Print a warning otherwise.
if os.path.isdir(FRONTEND_APP_BUILD_DIR):
    WHITENOISE_ROOT = FRONTEND_APP_BUILD_DIR
else:
    print(
        "Warning: FRONTEND_APP_BUILD_DIR does not exist. The frontend will not be served",
        file=sys.stderr,
    )
#: Root URL patterns
ROOT_URLCONF = "project.urls"

#: Template loading
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [FRONTEND_APP_BUILD_DIR],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
            ],
        },
    },
]

#: WSGI
WSGI_APPLICATION = "project.wsgi.application"


#: Password validation
#:
#: .. seealso:: https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


#: Internationalization
#:
#: .. seealso:: https://docs.djangoproject.com/en/2.0/topics/i18n/
LANGUAGE_CODE = "en-gb"

#: Internationalization
TIME_ZONE = "UTC"

#: Internationalization
USE_I18N = True

#: Internationalization
USE_TZ = True

#: Static files (CSS, JavaScript, Images)
#:
#: .. seealso:: https://docs.djangoproject.com/en/2.0/howto/static-files/
STATIC_URL = "/static/"

#: Authentication backends
AUTHENTICATION_BACKENDS = [
    "social_core.backends.google.GoogleOAuth2",
    "django.contrib.auth.backends.ModelBackend",
]

STATIC_ROOT = os.environ.get("DJANGO_STATIC_ROOT", os.path.join(BASE_DIR, "build", "static"))

# By default we a) redirect all HTTP traffic to HTTPS, b) set the HSTS header to a maximum age
# of 1 year (as per the consensus recommendation from a quick Google search) and c) advertise that
# we are willing to be "preloaded" into Chrome and Firefox's internal list of HTTPS-only sites.
# Set the DANGEROUS_DISABLE_HTTPS_REDIRECT variable to any non-blank value to disable this.
if os.environ.get("DANGEROUS_DISABLE_HTTPS_REDIRECT", "") == "":
    # Exempt the healtch-check endpoint from the HTTP->HTTPS redirect.
    SECURE_REDIRECT_EXEMPT = ["^healthy/?$"]

    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000  # == 1 year
    SECURE_HSTS_PRELOAD = True
else:
    print("Warning: HTTP to HTTPS redirect has been disabled.", file=sys.stderr)

# Whether to support the x_forwarded_host in constructing the canonical url.
# USE_X_FORWARDED_HOST = False

_structlog_foreign_pre_chain = [
    structlog.stdlib.add_log_level,
    structlog.stdlib.add_logger_name,
    structlog.processors.TimeStamper(fmt="iso"),
]


LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "formatters": {
        # This formatter logs as structured JSON suitable for use in Cloud hosting environments.
        "json_formatter": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.JSONRenderer(),
            "foreign_pre_chain": _structlog_foreign_pre_chain,
        },
        # This formatter logs as coloured text suitable for use by humans.
        "console_formatter": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.dev.ConsoleRenderer(colors=True),
            "foreign_pre_chain": _structlog_foreign_pre_chain,
        },
    },
    "handlers": {
        # If debug is enabled, we render using the pretty console formatter. If it is disabled we
        # render using the JSON formatter.
        "console": {
            "class": "logging.StreamHandler",
            "filters": ["require_debug_true"],
            "formatter": "console_formatter",
        },
        "json": {
            "class": "logging.StreamHandler",
            "filters": ["require_debug_false"],
            "formatter": "json_formatter",
        },
    },
    "loggers": {
        "": {
            "handlers": ["json", "console"],
            "propagate": True,
            "level": "INFO",
        },
    },
}

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)
