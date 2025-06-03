import sys
from contextvars import ContextVar

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

cloud_trace_context: ContextVar[str] = ContextVar("cloud_trace_context", default="")
http_request_context: ContextVar[dict] = ContextVar(
    "http_request_context", default=dict({})
)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        trace_context = request.headers.get("x-cloud-trace-context")
        if trace_context:
            cloud_trace_context.set(trace_context)

        http_request = {
            "requestMethod": request.method,
            "requestUrl": request.url.path,
            "requestSize": sys.getsizeof(request),
            "remoteIp": request.client.host if request.client else "",
            "protocol": request.url.scheme,
        }

        if "referrer" in request.headers:
            http_request["referrer"] = request.headers.get("referrer")

        if "user-agent" in request.headers:
            http_request["userAgent"] = request.headers.get("user-agent")

        http_request_context.set(http_request)

        return await call_next(request)
