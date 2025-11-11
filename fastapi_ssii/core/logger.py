# fastapi_ssii/core/logger.py
import logging
import json
from datetime import datetime, timezone

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            # Correction: Utiliser la méthode recommandée pour les timestamps UTC
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'level': record.levelname,
            'name': record.name,
            'message': record.getMessage(),
        }
        if hasattr(record, 'extra_data'):
            log_data.update(record.extra_data)
        return json.dumps(log_data)

class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        if not self.logger.handlers:
            self.logger.setLevel(logging.INFO)
            handler = logging.StreamHandler()
            handler.setFormatter(JsonFormatter())
            self.logger.addHandler(handler)

    def info(self, message: str, **kwargs):
        self.logger.info(message, extra={'extra_data': kwargs})

    def error(self, message: str, **kwargs):
        self.logger.error(message, extra={'extra_data': kwargs})

def get_logger(name: str) -> StructuredLogger:
    return StructuredLogger(name)
