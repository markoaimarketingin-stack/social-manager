import logging
import sys

from app.core.config import settings

try:
    from pythonjsonlogger.jsonlogger import JsonFormatter
except ModuleNotFoundError:  # pragma: no cover - fallback for lean environments
    JsonFormatter = None


def configure_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    if JsonFormatter is not None:
        formatter: logging.Formatter = JsonFormatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s %(path)s %(method)s %(status_code)s %(duration_ms)s"
        )
    else:
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(settings.log_level.upper())
