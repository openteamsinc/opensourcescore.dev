import logging
import re

from google.cloud.logging_v2.handlers import CloudLoggingFilter  # type: ignore

from .middleware import cloud_trace_context, http_request_context


class GoogleCloudLogFilter(CloudLoggingFilter):

    def filter(self, record: logging.LogRecord) -> bool:
        record.http_request = http_request_context.get()

        trace = cloud_trace_context.get()
        if trace and "/" in trace:
            split_header = trace.split("/", 1)
            record.trace = f"projects/{self.project}/traces/{split_header[0]}"
            header_suffix = split_header[1]
            record.span_id = re.findall(r"^\w+", header_suffix)[0]

        return super().filter(record)
