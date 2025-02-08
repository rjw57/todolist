# Import settings from the base settings file
from .base import *  # noqa: F401, F403

DEBUG = True


def _show_toolbar(request):
    from django.conf import settings

    return settings.DEBUG


# Configure the django debug toolbar if it is installed.
try:
    import debug_toolbar  # noqa: F401

    INSTALLED_APPS = INSTALLED_APPS + [  # noqa: F405
        "debug_toolbar",
    ]

    MIDDLEWARE = MIDDLEWARE + [  # noqa: F405
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ]

    DEBUG_TOOLBAR_CONFIG = {
        # Bypass the INTERNAL_IPS check since, within the development docker container, we don't
        # know what the host IP is likely to be.
        "SHOW_TOOLBAR_CALLBACK": _show_toolbar,
    }
except ImportError:
    pass

STATIC_URL = "/static/"
