import logging
from django.contrib.auth import logout
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext as _
from ml.utils import log_user_activity

logger = logging.getLogger(__name__)


class ActiveUserRequiredMixin(AccessMixin):
    """
    Verify that the current user is authenticated,
    active, and optionally restrict access based on
    staff status.
    """

    require_staff = False
    require_non_staff = False
    allow_both = False

    def dispatch(self, request, *args, **kwargs):
        user = request.user

        # Check if the user is authenticated and active
        if not user.is_authenticated or not user.is_active:
            logout(request)
            messages.error(request, _("Please log in to access this page."))
            return redirect("auth:login")

        # Check if the view is staff-only and the user is not staff
        if self.require_staff and not user.is_staff:
            log_user_activity(request, user, "Attempted access to staff-only page")
            logger.warning(
                f"403 Forbidden: User {user} attempted to access a staff-only page."
            )
            raise PermissionDenied(_("You do not have permission to access this page."))

        # Check if the view is non-staff-only and the user is staff
        if self.require_non_staff and user.is_staff:
            log_user_activity(request, user, "Attempted access to non-staff page")
            logger.warning(
                f"403 Forbidden: User {user} attempted to access a non-staff page."
            )
            raise PermissionDenied(_("You do not have permission to access this page."))

        # Ensure that `allow_both` is consistent with other flags
        if not self.allow_both and self.require_staff and self.require_non_staff:
            raise ValueError(
                "Cannot set both `require_staff` and `require_non_staff` to True without setting `allow_both` to True."
            )

        return super().dispatch(request, *args, **kwargs)


class ActiveUserRequiredMixin1(AccessMixin):
    """Verify that the current user is authenticated, active, and optionally a staff member."""

    require_staff = False

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_active:
            logout(request)
            messages.error(request, _("Please log in to access this page."))
            return redirect("auth:login")

        if self.require_staff and not request.user.is_staff:
            logout(request)
            messages.error(
                request,
                _(
                    "You do not have permission to access this page. Please contact your administrator."
                ),
            )
            return redirect("auth:login")

        return super().dispatch(request, *args, **kwargs)
