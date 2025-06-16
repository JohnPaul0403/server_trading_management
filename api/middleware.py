import logging
import time
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):
    """Middleware to log API requests"""

    def process_request(self, request):
        request.start_time = time.time()

        # Log request details
        logger.info(f"API Request: {request.method} {request.path}")

        if request.user.is_authenticated:
            logger.info(f"User: {request.user.email}")

    def process_response(self, request, response):
        # Calculate request duration
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            logger.info(f"API Response: {response.status_code} - Duration: {duration:.3f}s")

        return response
