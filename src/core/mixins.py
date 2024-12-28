from django.core.exceptions import PermissionDenied


class AdminRequiredMixin:
    """Mixin to check if the user is an admin."""

    def dispatch(self, request, *args, **kwargs):
        if not getattr(request.user, "is_admin", False):
            raise PermissionDenied  # Raises a 403 Forbidden error
        return super().dispatch(request, *args, **kwargs)
