from django.conf import settings
from django.core.checks import Error, register

REQUIRED_SETTINGS: list[str] = [
    # We use Google for sign in so ensure that the credentials are supplied and are non-empty.
    "SOCIAL_AUTH_GOOGLE_OAUTH2_KEY",
    "SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET",
]


@register
def required_settings_check(app_configs, **kwargs):
    """
    A system check ensuring that the required settings have non-empty values.

    .. seealso:: https://docs.djangoproject.com/en/2.0/ref/checks/

    """
    errors = []

    # Check that all required settings are specified and non-None
    for idx, name in enumerate(REQUIRED_SETTINGS):
        value = getattr(settings, name, None)
        if value is None or value == "":
            errors.append(
                Error(
                    "Required setting {} not set".format(name),
                    id="smi_project.E{:03d}".format(idx + 1),
                    hint="Add {} to settings.".format(name),
                )
            )

    return errors
