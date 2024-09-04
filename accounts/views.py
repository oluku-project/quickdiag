from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetConfirmView,
    PasswordResetConfirmView as AuthPasswordResetConfirmView,
)
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import CreateView, View, FormView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from PaulVideoPlatform.utils import PASSWORD_VALIDITY, MailUtils
from accounts.mixins import ActiveUserRequiredMixin
from ml.utils import log_user_activity
from patients.models import PredictionResult
from .forms import LoginForm, RegistrationForm, SetPasswordForm, UpdateAccountForm
from .models import Account
from django.contrib import auth
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import update_session_auth_hash
import logging
from django.db import transaction

logger = logging.getLogger("custom_logger")


class UserRegistrationView(MailUtils, CreateView):
    form_class = RegistrationForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("auth:login")

    def dispatch(self, request, *args, **kwargs):
        if not request.allow_registration:
            messages.info(
                request,
                _(
                    "We're sorry, but new registrations are currently not allowed. Please check back later or contact support for more information."
                ),
            )
            return redirect("auth:login")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            with transaction.atomic():
                user = form.save(commit=False)
                user.is_active = False
                password = form.cleaned_data.get("password")
                email = form.cleaned_data.get("email")
                user.username = str(email.split("@")[0])
                user.password = make_password(password)
                user.save()

                group, created = Group.objects.get_or_create(name="Users")
                if created:
                    group.save()
                user.groups.add(group)

                # Send activation email
                mail_temp = "accounts/account_verification_email.html"
                mail_subject = "Activate Your Account"
                self.compose_email(
                    self.request, user, mail_subject=mail_subject, mail_temp=mail_temp
                )

                self.request.session["registration_success"] = True
                log_user_activity(
                    self.request, user, "User registered and activation email sent"
                )
                return redirect(self.success_url)

        except Exception as e:
            # Delete the user if something goes wrong
            if user.pk:
                user.delete()
            logger.error(f"Error during registration: {e}", exc_info=True)
            messages.error(
                self.request,
                _("An error occurred during registration. Please try again."),
            )
            return self.form_invalid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, _(f"{field}: {error}"))
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title_root"] = _("Sign Up")
        return context


userregistrationview = UserRegistrationView.as_view()


class ActivateAccountView(View):

    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = get_object_or_404(Account, pk=uid)

            if user is not None and default_token_generator.check_token(user, token):
                user.is_active = True
                user.save()
                log_user_activity(request, user, "User activated their account")
                messages.success(
                    request, _("Congratulations! Your account is activated.")
                )
                return redirect("auth:login")
            else:
                messages.error(request, _("Invalid activation link"))
                return redirect("auth:signup")

        except Exception as e:
            logger.error(f"Error during account activation: {e}", exc_info=True)
            messages.error(
                request,
                _("An error occurred during account activation. Please try again."),
            )
            return redirect("auth:signup")


activateaccountview = ActivateAccountView.as_view()

User = auth.get_user_model()


class LoginView(FormView):
    template_name = "accounts/login.html"
    form_class = LoginForm

    def redirect_to_staff_dashboard(self):
        return redirect(reverse_lazy("AdminHub:dashboard"))

    def redirect_to_user_dashboard(self):
        return redirect(reverse_lazy("auth:user_dashboard"))

    def form_valid(self, form):
        try:
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = auth.authenticate(email=username, password=password)
            if user is not None:
                auth.login(self.request, user)
                log_user_activity(self.request, user, "User logged in successfully")
                messages.success(self.request, _("You are now logged in."))
                if user.is_staff:
                    return self.redirect_to_staff_dashboard()
                else:
                    return self.redirect_to_user_dashboard()
            else:
                log_user_activity(
                    self.request,
                    None,
                    f"Failed login attempt with username: {username}",
                )
                messages.error(self.request, _("Invalid login credentials."))
                return self.form_invalid(form)
        except Exception as e:
            logger.error(f"Error during login: {e}", exc_info=True)
            messages.error(
                self.request, _("An error occurred during login. Please try again.")
            )
            return self.form_invalid(form)

    def form_invalid(self, form):
        try:
            user = User.objects.get(email=form.cleaned_data.get("username"))
            if user.is_active:
                messages.error(
                    self.request, _("Invalid credentials. Please try again.")
                )
            else:
                messages.error(
                    self.request,
                    _(
                        "Your account is inactive. Please check your email for activation instructions."
                    ),
                )
        except User.DoesNotExist:
            messages.error(
                self.request,
                _(
                    "Invalid email credentials. Please try signing up if have no account."
                ),
            )
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title_root"] = "Login"
        return context


loginview = LoginView.as_view()


class LogoutView(ActiveUserRequiredMixin, View):
    allow_both = True

    def get(self, request):
        try:
            log_user_activity(request, request.user, "User logged out")
            auth.logout(request)
            messages.success(request, _("You are logged out."))
            return redirect("auth:login")
        except Exception as e:
            logger.error(f"Error during logout: {e}", exc_info=True)
            messages.error(
                request, _("An error occurred during logout. Please try again.")
            )
            return redirect("auth:login")


logoutview = LogoutView.as_view()


class ForgotPasswordView(MailUtils, View):
    template_name = "accounts/forgotPassword.html"

    def get(self, request):
        return render(request, self.template_name, {"title_root": "Forgot Password"})

    def post(self, request):
        try:
            email = request.POST.get("email")
            if Account.objects.filter(email=email).exists():
                user = Account.objects.get(email__exact=email)
                mail_temp = "accounts/reset_password_email.html"
                mail_subject = "Reset Your Password"
                self.compose_email(
                    self.request, user, mail_subject=mail_subject, mail_temp=mail_temp
                )
                log_user_activity(request, user, "Requested password change")
                messages.success(
                    request,
                    _("Password reset email has been sent to your email address."),
                )
                return redirect("auth:login")
            else:
                log_user_activity(
                    request,
                    None,
                    f"Password reset attempt with non-existing email: {email}",
                )
                messages.error(request, _("Account does not exist!"))
                return redirect("auth:forgotPassword")

        except Exception as e:
            logger.error(f"Error during password reset request: {e}", exc_info=True)
            messages.error(
                request,
                _(
                    "An error occurred during the password reset request. Please try again."
                ),
            )
            return redirect("auth:forgotPassword")


forgotpasswordview = ForgotPasswordView.as_view()


class PasswordResetConfirmView(AuthPasswordResetConfirmView):
    allow_both = True
    form_class = SetPasswordForm
    template_name = "accounts/password_reset_confirm.html"
    success_url = reverse_lazy("auth:password_reset_complete")

    def form_valid(self, form):
        try:
            user = form.save()
            log_user_activity(self.request, user, "Password reset completed")
            messages.success(
                self.request,
                _(
                    "Your password has been reset successfully. You can now log in with your new password."
                ),
            )
            return super().form_valid(form)
        except Exception as e:
            logger.error(
                f"Error during password reset confirmation: {e}", exc_info=True
            )
            messages.error(
                self.request,
                _(
                    "An error occurred during password reset confirmation. Please try again."
                ),
            )
            return self.form_invalid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field}: {error}")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title_root"] = _("Reset Password")
        return context


passwordresetconfirmview = PasswordResetConfirmView.as_view()


class PasswordResetCompleteView(TemplateView):
    template_name = "accounts/password_reset_complete.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title_root"] = _("Password Reset Complete - Breast Cancer Prediction")
        return context


passwordresetcompleteview = PasswordResetCompleteView.as_view()


class PrivacyView(TemplateView):
    template_name = "accounts/privacy.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        log_user_activity(self.request, self.request.user, "viewed privacy page")
        context["title_root"] = _("Privacy")
        return context


privacyview = PrivacyView.as_view()


class TermsView(TemplateView):
    template_name = "accounts/terms.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        log_user_activity(self.request, self.request.user, "viewed terms page")
        context["title_root"] = _("Terms")
        return context


termsview = TermsView.as_view()


class UserDashboardView(ActiveUserRequiredMixin, TemplateView):
    allow_both = True
    template_name = "accounts/user-dashboard.html"

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            latest_prediction = (
                PredictionResult.objects.filter(user=self.request.user)
                .order_by("-submission_date")
                .first()
            )
            from django.db.models import Avg, Sum
            from django.db.models.functions import TruncMonth

            # Area chart data: Group by month and sum risk scores
            monthly_data = (
                PredictionResult.objects.filter(user=self.request.user)
                .annotate(month=TruncMonth("submission_date"))
                .values("month")
                .annotate(
                    total_risk_score=Sum("risk_score"), avg_risk_score=Avg("risk_score")
                )
                .order_by("month")
            )

            months = [
                "Jan",
                "Feb",
                "Mar",
                "Apr",
                "May",
                "Jun",
                "Jul",
                "Aug",
                "Sep",
                "Oct",
                "Nov",
                "Dec",
            ]

            area_chart_data = [0] * 12
            avg_chart_data = [0] * 12

            for data in monthly_data:
                month_idx = data["month"].month - 1  # Convert month to zero-based index
                area_chart_data[month_idx] = float(round(data["total_risk_score"], 2))
                avg_chart_data[month_idx] = float(round(data["avg_risk_score"], 2))

            # Donut chart data: Group by risk level and sum risk scores
            risk_levels = ["High", "Moderate", "Low"]
            risk_data = (
                PredictionResult.objects.filter(user=self.request.user)
                .values("risk_level")
                .annotate(total_risk_score=Sum("risk_score"))
            )

            risk_scores = {level: 0.0 for level in risk_levels}
            for data in risk_data:
                risk_scores[data["risk_level"]] = float(
                    round(data["total_risk_score"], 2)
                )

            donut_chart_data = [risk_scores[level] for level in risk_levels]

            # Additional Data
            overall_risk_score = (
                PredictionResult.objects.filter(user=self.request.user).aggregate(
                    Sum("risk_score")
                )["risk_score__sum"]
                or 0
            )
            total_predictions = PredictionResult.objects.filter(
                user=self.request.user
            ).count()
            high_risk_predictions = PredictionResult.objects.filter(
                user=self.request.user, risk_level="High"
            ).count()
            last_prediction_date = (
                latest_prediction.submission_date if latest_prediction else "N/A"
            )

            log_user_activity(self.request, self.request.user, "viewed dashboard page")
            context["area_chart_data"] = area_chart_data
            context["avg_chart_data"] = avg_chart_data
            context["area_chart_labels"] = months
            context["donut_chart_data"] = donut_chart_data
            context["donut_chart_labels"] = risk_levels
            context["overall_risk_score"] = float(overall_risk_score)
            context["total_predictions"] = total_predictions
            context["high_risk_predictions"] = high_risk_predictions
            context["last_prediction_date"] = last_prediction_date
            context["result"] = latest_prediction
            context["title_root"] = _("User Dashboard")
            return context
        except Exception as e:
            logger.error(f"Error loading dashboard data: {e}", exc_info=True)
            messages.error(
                self.request,
                _("An error occurred while loading your dashboard. Please try again."),
            )
            return self.render_to_response(self.get_context_data())


userdashboardview = UserDashboardView.as_view()


class UpdateAccountView(ActiveUserRequiredMixin, View):
    allow_both = True
    template_name = "accounts/profile.html"

    def get(self, request, *args, **kwargs):
        user = get_object_or_404(Account, pk=request.user.pk)
        context = self.getContext(user)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        user = get_object_or_404(Account, pk=request.user.pk)

        try:
            if "update_profile" in request.POST:
                form = UpdateAccountForm(request.POST, instance=user)
                form_type = "profile"
            elif "change_password" in request.POST:
                form = SetPasswordForm(user=user, data=request.POST)
                form_type = "password"

            if form.is_valid():
                form.save()
                log_user_activity(request, request.user, "updated account")
                msg = "Account updated sucessfully"
                if form_type == "password":
                    update_session_auth_hash(request, form.user)
                    log_user_activity(request, request.user, "updated password")
                    msg = "Password updated successfully."
                messages.success(request, msg)
                return redirect("auth:profile")
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(self.request, f"{field}: {error}")
        except:
            logger.error(f"Error updating account: {e}", exc_info=True)
            messages.error(
                request,
                "An error occurred while updating your account. Please try again.",
            )
        context = self.getContext(user)
        return render(request, self.template_name, context)

    def getContext(self, user):
        update_form = UpdateAccountForm(instance=user)
        password_form = SetPasswordForm(user=user)

        context = {
            "update_form": update_form,
            "password_form": password_form,
            "validity": PASSWORD_VALIDITY,
            "title_root": "Profile",
        }
        return context


updateaccountview = UpdateAccountView.as_view()
