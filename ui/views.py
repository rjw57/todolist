from typing import Optional, Any
from urllib.parse import urlsplit, urlunsplit

import requests
import structlog
from django.conf import settings
from django.http import HttpRequest, StreamingHttpResponse
from django.views import View

LOG = structlog.get_logger()


def _stream_requests_response(response: requests.Response):
    return StreamingHttpResponse(
        response.iter_content(chunk_size=1<<20),
        status=response.status_code,
        content_type=response.headers["Content-Type"],
    )


def _url_for_frontend_path(path: str) -> str:
    base_url = getattr(settings, "FRONTEND_SERVER", None)
    if base_url is None:
        raise RuntimeError("FRONTEND_SERVER setting not set and is required when serving the UI.")

    components = urlsplit(base_url)
    return urlunsplit((components[0], components[1], path, "", ""))


def proxy_to_frontend(request: HttpRequest, *, path: Optional[str] = None):
    path = request.get_full_path().lstrip("/") if path is None else path
    url = _url_for_frontend_path(path)
    assert request.method is not None

    response = requests.request(request.method, url, data=request.body, stream=True)
    return _stream_requests_response(response)


class FrontendView(View):
    path: Optional[str] = None

    def get_context_data(self, request, *args, **kwargs) -> dict[str, Any]:
        return {}

    def dispatch(self, request, *args, **kwargs):
        path = request.path if self.path is None else self.path
        url = _url_for_frontend_path(path)
        response = requests.post(
            url,
            json={
                "context": self.get_context_data(request, *args, **kwargs),
            },
            headers={"X-Requested-With": "django"},
            stream=True,
        )
        # TODO: maybe revert to non-streaming to support Django Debug Toolbar?
        return _stream_requests_response(response)


class TemplateTest(FrontendView):
    path = "template-test"

    def get_context_data(self, request, *args, template_id: str = "", **kwargs) -> dict:
        return {"GET": request.GET, "templateId": template_id}
