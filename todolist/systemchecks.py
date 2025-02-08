"""
The :py:mod:`todolist` application ships with some custom system
checks which ensure that required settings are present. These system checks are registered by
the :py:class:`~todolist.apps.Config` class's
:py:meth:`~todolist.apps.AssetsConfig.ready` method.

.. seealso::

    The `Django System Check Framework <https://docs.djangoproject.com/en/2.0/ref/checks/>`_.

"""
from django.conf import settings
from django.core.checks import Error, register

REQUIRED_SETTINGS: list[str] = [
    # ... TODO: add any required settings here
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
                    id="todolist.E{:03d}".format(idx + 1),
                    hint="Add {} to settings.".format(name),
                )
            )

    return errors
