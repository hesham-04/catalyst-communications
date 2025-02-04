from sentry_sdk import set_context
from django.utils.timezone import now
import logging

logger = logging.getLogger(__name__)

class SentryUserContextMiddleware:
    """
    Middleware to capture user context (for authenticated and unauthenticated users)
    and send it to Sentry for error reporting.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """
        This method is called for each request.
        It attaches user information to the Sentry scope.
        """
        self._set_user_context(request)
        response = self.get_response(request)
        return response

    def _set_user_context(self, request):
        """
        Sets the user context in Sentry with user details if available.
        Captures user ID, username, email, first_name, last_name, role, bio, is_admin, IP address, and user agent.
        """
        try:
            if request.user.is_authenticated:
                set_context(
                    "user", {
                    'id': request.user.id,
                    'username': request.user.username,
                    'email': request.user.email,
                    'first_name': request.user.first_name,
                    'last_name': request.user.last_name,
                    'bio': request.user.bio,
                    'role': request.user.role,
                    'is_admin': request.user.is_admin,
                })
            else:
                set_context("user", {
                    'id': None,
                    'username': 'Anonymous',
                    'email': 'N/A',
                })

            set_context('contexts', {
                'IP Address': {'ip': self._get_client_ip(request)},
                'User-Agent': {'user_agent': request.META.get('HTTP_USER_AGENT', 'Unknown')},
                'Request Timestamp': {'timestamp': now().isoformat()},
            })

        except Exception as e:
            logger.error(f"Failed to set user context for Sentry: {e}")

    def _get_client_ip(self, request):
        """
        Tries to get the real IP address of the client from the request headers.
        This is especially useful behind proxies or load balancers.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
