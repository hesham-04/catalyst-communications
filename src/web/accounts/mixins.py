from django.contrib.auth.mixins import AccessMixin
from django.http import HttpResponseForbidden

class SuperuserRequiredMixin(AccessMixin):
    """Mixin to allow only superusers to access a view."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return HttpResponseForbidden("You do not have permission to access this page.")
        return super().dispatch(request, *args, **kwargs)