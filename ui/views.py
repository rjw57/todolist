from typing import Optional
from urllib.parse import urlsplit, urlunsplit

import requests
import structlog
from django.http import HttpRequest, HttpResponse
from django.views import View

from .render import ensure_frontend_server

LOG = structlog.get_logger()


def _forward_requests_response(response: requests.Response):
    return HttpResponse(
        response.content,
        status=response.status_code,
        content_type=response.headers["Content-Type"],
    )


def _session_and_url_for_frontend_path(path: str) -> tuple[requests.Session, str]:
    frontend = ensure_frontend_server()
    if frontend is None:
        raise RuntimeError("No frontend server configured.")

    session, base_url = frontend.get_session_and_base_url()
    components = urlsplit(base_url)
    url = urlunsplit((components[0], components[1], path, "", ""))

    return session, url


def proxy_to_frontend(request: HttpRequest, *, path: Optional[str] = None) -> HttpResponse:
    path = request.get_full_path().lstrip("/") if path is None else path
    session, url = _session_and_url_for_frontend_path(path)
    assert request.method is not None

    response = session.request(request.method, url, data=request.body)
    return _forward_requests_response(response)


class FrontendView(View):
    path: Optional[str] = None

    def get_context_data(self, request, *args, **kwargs) -> dict:
        return {}

    def dispatch(self, request, *args, **kwargs):
        path = request.path if self.path is None else self.path
        session, url = _session_and_url_for_frontend_path(path)
        response = session.post(
            url,
            json={
                "context": self.get_context_data(request, *args, **kwargs),
            },
            headers={
                "X-Requested-With": "django",
            },
        )
        return _forward_requests_response(response)
