"""
URL routing schema for UI

"""

from django.conf import settings
from django.urls import path, re_path

from . import views

app_name = "ui"

urlpatterns = [
    path("", views.FrontendView.as_view(), name="home"),
    path("another-index", views.FrontendView.as_view(path=""), name="another-index"),
    path("template-test", views.FrontendView.as_view(), name="another-index"),
]

# If we were passed an additional list of path regexes to pass to the frontend server, configure
# those routes.
if getattr(settings, "FRONTEND_ADDITIONAL_FORWARDED_PATH_REGEX", None) is not None:
    urlpatterns.append(
        re_path(
            settings.FRONTEND_ADDITIONAL_FORWARDED_PATH_REGEX,
            views.proxy_to_frontend,
            name="addititional-frontend",
        )
    )
