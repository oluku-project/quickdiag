import logging
from django.urls import reverse
from django.shortcuts import render, redirect
from django.db import transaction
from accounts.mixins import ActiveUserRequiredMixin
from accounts.templatetags.custom_filters import calculate_age
from ml.models import GeneralSettings
from ml.utils import log_user_activity
from patients.forms import ContactForm, FeedbackForm
from patients.utils import (
    QUESTIONS,
    HelpResponse,
    section_headers,
    RISK_LEVEL,
    CATEGORIES,
    FAQS,
)
from django.http import HttpResponse, JsonResponse
from django.views.generic import DetailView, View, TemplateView
from typing import List
from django.shortcuts import get_object_or_404
from .models import STATE, PredictionResult, QuestionnaireResponse, Response
from PaulVideoPlatform import settings
import pandas as pd
import pickle5 as pickle
from django_filters.views import FilterView
from .filters import PredictionResultFilter, QuestionnaireResponseFilter
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
)
from django.contrib import messages
from io import BytesIO
import matplotlib.pyplot as plt
import base64
from django.utils.translation import gettext_lazy as _


logger = logging.getLogger("custom_logger")


class QuestionnaireView(ActiveUserRequiredMixin, View):
    require_non_staff = True
    template_name = "patients/questionnaire.html"
    responseID = None

    def dispatch(self, request, *args, **kwargs):
        # Calculate user's age
        response = super().dispatch(request, *args, **kwargs)
        if not request.user.is_authenticated:
            # If not authenticated, this should be handled by the mixin, but you can add custom behavior here if needed
            messages.error(request, _("You need to be logged in to access this page."))
            return redirect("auth:login")

        # Ensure the user has a date of birth
        if request.user.date_of_birth is None:
            messages.error(
                request,
                _(
                    "We could not retrieve your date of birth. Please update your profile."
                ),
            )
            return redirect("auth:profile")

        # Calculate user's age
        user_age = calculate_age(request.user.date_of_birth)
        if user_age < 18:
            messages.error(
                request,
                _(
                    "You must be at least 18 years old to complete the questionnaire. Please update your profile if this information is incorrect."
                ),
            )
            return redirect("auth:profile")

        return response

    def get(self, request, *args, **kwargs):
        self.responseID = kwargs.get("pk", None)
        return render(request, self.template_name, self.get_context())

    def post(self, request, *args, **kwargs):
        self.responseID = kwargs.get("pk", None)

        # Extract form data
        form_data = request.POST
        progress = form_data.get("progress", 0)

        # Filter out questions with "Yes" responses (where answer is "on")
        responses = {key: value for key, value in form_data.items() if value == "on"}
        if responses:
            # Save responses to the database
            response_instance, msg = self.save_responses(
                request.user,
                responses,
                progress,
            )
            # Add a success message
            messages.success(request, msg)
            return redirect(reverse("summary", kwargs={"pk": response_instance.id}))

        return render(request, self.template_name, self.get_context())

    def get_context(self):
        question_keys = (
            self.get_question_keys_for_response(self.responseID)
            if self.responseID
            else None
        )
        context = {
            "questions": QUESTIONS,
            "section_headers": section_headers,
            "question_keys": question_keys,
            "title_root": "Questionnaire",
        }
        return context

    def save_responses(self, user, responses, progress):
        # Start a transaction to ensure atomicity
        with transaction.atomic():
            # Check if responseID is provided
            if self.responseID:
                # Try to retrieve the existing QuestionnaireResponse instance
                response_instance = QuestionnaireResponse.objects.get(
                    id=self.responseID
                )

                # Delete existing responses
                response_instance.responses.all().delete()

                # Update progress if it has changed
                if response_instance.progress != progress:
                    response_instance.progress = progress
                    response_instance.save()
                    log_user_activity(
                        self.request, user, "Updated responses for the assessment."
                    )
                    msg = "Your responses have been updated and successfully submitted."
            else:
                # Create a new QuestionnaireResponse instance
                response_instance = QuestionnaireResponse.objects.create(
                    user=user, progress=progress, created_by=user
                )
                log_user_activity(self.request, user, "Initiated a new assessment.")
                msg = "Your responses have been created successfully."
            # Create new responses for the QuestionnaireResponse instance
            response_objects = [
                Response(questionnaire_response=response_instance, question_key=key)
                for key in responses.keys()
            ]
            Response.objects.bulk_create(response_objects)

        return response_instance, msg

    def get_question_keys_for_response(self, pk) -> List[str]:
        response_instance = get_object_or_404(QuestionnaireResponse, pk=pk)
        # Retrieve all related Response instances and extract question_key as a list
        question_keys = response_instance.responses.all().values_list(
            "question_key",
            flat=True,
        )
        return list(question_keys)


questionnaier = QuestionnaireView.as_view()


class SummaryView(ActiveUserRequiredMixin, HelpResponse, DetailView):
    allow_both = True
    model = QuestionnaireResponse
    template_name = "patients/summary.html"
    context_object_name = "response_instance"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        response_instance = self.object

        grouped_questions = self.fetchRespondedQuestions(response_instance)
        context.update(
            {
                "grouped_questions": grouped_questions,
                "section_headers": section_headers,
                "title_root": "Summary",
            }
        )
        response_instance.state = STATE.IN_PROGRESS
        response_instance.save()
        log_user_activity(
            self.request, self.request.user, "Viewed summary of the assessment."
        )
        return context


summary_view = SummaryView.as_view()


class PredictionView(ActiveUserRequiredMixin, HelpResponse, DetailView):
    allow_both = True

    template_name = "patients/results.html"
    context_object_name = "response_instance"

    def get_queryset(self):
        """
        Override to return different querysets based on URL name.
        """
        if self.request.resolver_match.url_name == "detailed_result":
            return PredictionResult.objects.all()
        return QuestionnaireResponse.objects.all()

    def get_object(self, queryset=None):
        """
        Override to get the object based on the dynamic model.
        """
        if self.request.resolver_match.url_name == "detailed_result":
            return get_object_or_404(PredictionResult, pk=self.kwargs["pk"])
        else:
            return get_object_or_404(QuestionnaireResponse, pk=self.kwargs["pk"])

    def get_line_scatter_chart(self, input_data):
        input_data = self.get_scaled_values(input_data)
        mean = [
            round(input_data["radius_mean"], 2),
            round(input_data["texture_mean"], 2),
            round(input_data["perimeter_mean"], 2),
            round(input_data["area_mean"], 2),
            round(input_data["smoothness_mean"], 2),
            round(input_data["compactness_mean"], 2),
            round(input_data["concavity_mean"], 2),
            round(input_data["concave points_mean"], 2),
            round(input_data["symmetry_mean"], 2),
            round(input_data["fractal_dimension_mean"], 2),
        ]
        standard = [
            round(input_data["radius_se"], 2),
            round(input_data["texture_se"], 2),
            round(input_data["perimeter_se"], 2),
            round(input_data["area_se"], 2),
            round(input_data["smoothness_se"], 2),
            round(input_data["compactness_se"], 2),
            round(input_data["concavity_se"], 2),
            round(input_data["concave points_se"], 2),
            round(input_data["symmetry_se"], 2),
            round(input_data["fractal_dimension_se"], 2),
        ]
        worst = [
            round(input_data["radius_worst"], 2),
            round(input_data["texture_worst"], 2),
            round(input_data["perimeter_worst"], 2),
            round(input_data["area_worst"], 2),
            round(input_data["smoothness_worst"], 2),
            round(input_data["compactness_worst"], 2),
            round(input_data["concavity_worst"], 2),
            round(input_data["concave points_worst"], 2),
            round(input_data["symmetry_worst"], 2),
            round(input_data["fractal_dimension_worst"], 2),
        ]

        chart_data = {
            "categories": CATEGORIES,
            "mean": mean,
            "standard": standard,
            "worst": worst,
        }

        return chart_data

    def display_explanations(self):
        return {
            "Mean Value": "Average or typical measurement for each category",
            "Standard Error": "Measure of variability or dispersion of the data",
            "Worst Value": "Worst-case scenario or maximum measurement observed for each category",
        }

    def save_prediction_result(
        self, user, response_instance, risk_level, risk_score, probabilities, chart_data
    ):
        existing_result = PredictionResult.objects.filter(
            user=user, questionnaire_response=response_instance
        ).first()

        if existing_result:
            # Update the existing result
            existing_result.risk_level = risk_level["level"]
            existing_result.risk_score = risk_score
            existing_result.dob = user.date_of_birth
            existing_result.probability_benign = probabilities[0][0]
            existing_result.probability_malignant = probabilities[0][1]
            existing_result.chart_data = chart_data
            existing_result.save()
        else:
            # Create a new prediction result
            PredictionResult.objects.create(
                user=user,
                questionnaire_response=response_instance,
                dob=user.date_of_birth,
                risk_level=risk_level["level"],
                risk_score=risk_score,
                probability_benign=probabilities[0][0],
                probability_malignant=probabilities[0][1],
                chart_data=chart_data,
            )
            response_instance.state = STATE.COMPLETED
            response_instance.save()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        response_instance = self.object
        explanations = self.display_explanations()

        url_name = self.request.resolver_match.url_name
        if url_name == "detailed_result":
            score = response_instance.risk_score
            risk_level, risk_score = self.make_prediction(risk_score=score)
            probability_benign = response_instance.probability_benign
            probability_malignant = response_instance.probability_malignant
            chart_data = response_instance.chart_data
            log_user_activity(
                self.request,
                self.request.user,
                "Viewed detailed results of the assessment.",
            )
            grouped_questions = self.fetchRespondedQuestions(
                response_instance.questionnaire_response
            )
            title = "Detailed Result"
        else:
            question_keys = response_instance.responses.all().values_list(
                "question_key",
                flat=True,
            )
            # Load default values
            data = self.get_clean_data()
            user_responses = {}
            for _, k, v in QUESTIONS:
                user_responses[k] = v if k in question_keys else float(data[k].mean())
            probabilities, _ = self.add_predictions(user_responses)
            chart_data = self.get_line_scatter_chart(user_responses)
            risk_level, risk_score = self.make_prediction(probabilities)
            risk_score = f"{risk_score * 100:.2f}"

            # Save the prediction result
            self.save_prediction_result(
                self.request.user,
                response_instance,
                risk_level,
                risk_score,
                probabilities,
                chart_data,
            )
            probability_benign = f"{probabilities[0][0]:.2f}"
            probability_malignant = f"{probabilities[0][1]:.2f}"
            grouped_questions = None
            log_user_activity(
                self.request,
                self.request.user,
                "Completed an assessment and viewed the results.",
            )
            title = "Result"

        # Store data in session
        self.storeDataInSession(response_instance, url_name)

        context.update(
            {
                "risk_level": risk_level,
                "risk_score": risk_score,
                "probability_benign": probability_benign,
                "probability_malignant": probability_malignant,
                "risk_explanation": explanations,
                "chart_data": chart_data,
                "response_instance": response_instance,
                "grouped_questions": grouped_questions,
                "title_root": title,
            }
        )

        return context

    def storeDataInSession(self, response_instance, url_name):
        prediction_data = self.request.session.get("input_data")
        if prediction_data:
            # Clear the session data after accessing it
            del self.request.session["input_data"]
        data = {
            "url_name": url_name,
            "pk": response_instance.pk,
        }
        self.request.session["input_data"] = data


results = PredictionView.as_view()


class PDFReportView(ActiveUserRequiredMixin, HelpResponse, View):
    allow_both = True

    def get_data(self):
        """Retrieve data from session and prepare it for the PDF report."""
        data = self.request.session.get("input_data")
        if not data:
            return HttpResponse("No prediction data found in session.", status=400)

        pk = data["pk"]
        url = data["url_name"]

        if url == "result":
            response_instance = get_object_or_404(QuestionnaireResponse, pk=pk)
            response_instance = get_object_or_404(
                PredictionResult, questionnaire_response=response_instance
            )
        else:
            response_instance = get_object_or_404(PredictionResult, pk=pk)

        score = response_instance.risk_score
        scores = score / 100
        risk_level, risk_score = self.make_prediction(risk_score=scores)
        probability_benign = response_instance.probability_benign
        probability_malignant = response_instance.probability_malignant
        chart_data = response_instance.chart_data

        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "score": score,
            "probability_benign": probability_benign,
            "probability_malignant": probability_malignant,
            "chart_data": chart_data,
            "response_instance": response_instance,
        }

    def generate_chart(self, chart_data):
        categories = chart_data["categories"]
        mean = chart_data["mean"]
        standard = chart_data["standard"]
        worst = chart_data["worst"]

        fig, ax = plt.subplots(figsize=(10, 6))

        # Bar chart for Mean Values
        ax.bar(
            categories,
            mean,
            color="skyblue",
            label="Mean Values",
            alpha=0.85,
            zorder=2,
            width=0.5,
        )

        # Area chart for Standard Error
        x = list(range(len(categories)))
        ax.fill_between(
            x,
            [m - s for m, s in zip(mean, standard)],
            [m + s for m, s in zip(mean, standard)],
            color="lightgreen",
            alpha=0.25,
            label="Standard Error",
            zorder=1,
        )

        # Line chart for Worst Values
        ax.plot(
            categories,
            worst,
            color="darkred",
            linewidth=2,
            marker="o",
            label="Worst Values",
            zorder=3,
            linestyle="--",
        )

        # Customizing the chart
        ax.set_xlabel("Features", fontsize=12)
        ax.set_ylabel("Values", fontsize=12)
        ax.set_title("Breast Cancer Prediction Data", fontsize=16, fontweight="bold")
        ax.legend(fontsize=10)
        ax.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.7)
        ax.set_xticklabels(categories, rotation=45, ha="right")

        plt.tight_layout()

        chart_image = BytesIO()
        plt.savefig(chart_image, format="png")
        chart_image.seek(0)
        chart_base64 = base64.b64encode(chart_image.read()).decode("utf-8")
        plt.close()

        return chart_base64

    def generate_pdf(self):
        data = self.get_data()
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        doc.title = "Breast Cancer Prediction Report"
        elements = []
        styles = getSampleStyleSheet()

        # Custom styles
        custom_styles = {
            "title": ParagraphStyle(
                "Title", fontSize=24, spaceAfter=30, alignment=1, fontWeight="bold"
            ),
            "heading1": ParagraphStyle(
                "Heading1", fontSize=18, spaceAfter=22, alignment=1
            ),
            "heading2": ParagraphStyle(
                "Heading2", fontSize=16, spaceAfter=16, alignment=1
            ),
            "heading3": ParagraphStyle(
                "Heading3", fontSize=14, spaceAfter=10, alignment=1
            ),
            "body": ParagraphStyle("Body", fontSize=12, spaceAfter=10),
            "small": ParagraphStyle("Small", fontSize=10, spaceAfter=8),
        }

        # Title Page
        elements.append(
            Paragraph("Breast Cancer Prediction Report", custom_styles["title"])
        )
        elements.append(
            Paragraph(
                "Generated for: {}".format(data["response_instance"].user.full_name()),
                custom_styles["heading2"],
            )
        )
        elements.append(
            Paragraph(
                "Date: {}".format(
                    data["response_instance"].submission_date.strftime("%B %d, %Y")
                ),
                custom_styles["heading3"],
            )
        )
        elements.append(Spacer(1, 30))

        # User Information
        elements.append(Paragraph("User Information", custom_styles["heading1"]))
        user_info = [
            ["Name", data["response_instance"].user.full_name()],
            ["Gender", data["response_instance"].user.gender],
            ["Age", calculate_age(data["response_instance"].dob)],
            [
                "Health History",
                data["response_instance"].questionnaire_response.progress,
            ],
        ]
        user_info_table = Table(user_info, hAlign="CENTER")
        user_info_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f2f2f2")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("TOPPADDING", (0, 0), (-1, 0), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                ]
            )
        )
        elements.append(user_info_table)
        elements.append(Spacer(1, 20))

        # Risk Assessment Summary
        elements.append(Paragraph("Risk Assessment Summary", custom_styles["heading1"]))
        risk_level = data["risk_level"]
        elements.append(
            Paragraph(f"Risk Level: {risk_level['info']}", custom_styles["body"])
        )
        elements.append(
            Paragraph(f"Risk Score: {data['risk_score']}", custom_styles["body"])
        )
        elements.append(Spacer(1, 20))

        # Probability Assessment
        elements.append(Paragraph("Probability Assessment", custom_styles["heading1"]))
        prob_info = [
            [
                "Probability of Being Benign",
                "{:.2f}%".format(data["probability_benign"] * 100),
            ],
            [
                "Probability of Being Malignant",
                "{:.2f}%".format(data["probability_malignant"] * 100),
            ],
        ]
        prob_info_table = Table(prob_info, hAlign="CENTER")
        prob_info_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f2f2f2")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("TOPPADDING", (0, 0), (-1, 0), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                ]
            )
        )
        elements.append(prob_info_table)
        elements.append(Spacer(1, 20))

        # Visual Analysis
        elements.append(Paragraph("Visual Analysis", custom_styles["heading1"]))
        chart_base64 = self.generate_chart(data["chart_data"])
        chart_img = Image(
            BytesIO(base64.b64decode(chart_base64)), width=500, height=300
        )
        elements.append(chart_img)
        elements.append(
            Paragraph(
                "The chart above represents your breast cancer risk assessment based on the selected features.",
                custom_styles["body"],
            )
        )
        elements.append(Spacer(1, 20))

        # Recommendations
        elements.append(Paragraph("Recommendations", custom_styles["heading1"]))
        elements.append(
            Paragraph(
                "Based on your assessment, we suggest the following steps.",
                custom_styles["body"],
            )
        )
        for rec in risk_level["recommendations"]:
            elements.append(Paragraph(rec["title"], custom_styles["heading2"]))
            elements.append(Paragraph(rec["message"], custom_styles["body"]))
        elements.append(Spacer(1, 20))

        # Next Steps
        elements.append(Paragraph("Next Steps", custom_styles["heading1"]))
        elements.append(Paragraph(risk_level["next"], custom_styles["body"]))
        for ns in risk_level["next_steps"]:
            elements.append(Paragraph(ns["subtitle"], custom_styles["heading2"]))
            for msg in ns["messages"]:
                elements.append(Paragraph(msg, custom_styles["body"]))
        elements.append(Spacer(1, 30))

        # Limitations
        elements.append(Paragraph("Limitations", custom_styles["heading1"]))
        limitations = [
            "Model limitations: This model is not perfect and should not be used as the sole basis for medical decisions.",
            "Data quality: The accuracy of the predictions depends on the quality of the input data.",
        ]
        for lim in limitations:
            elements.append(Paragraph(lim, custom_styles["body"]))

        # Footer
        elements.append(Spacer(1, 40))
        elements.append(
            Paragraph(
                "This report is generated based on the input data provided. For a more detailed analysis, consult a healthcare professional.",
                custom_styles["small"],
            )
        )
        elements.append(
            Paragraph(
                "Confidentiality Notice: This report contains sensitive information. Handle with care.",
                custom_styles["small"],
            )
        )
        elements.append(Spacer(1, 30))
        elements.append(
            Paragraph(
                f"Created By {self.request.user.username}", custom_styles["small"]
            )
        )

        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()
        return pdf


class PDFReportDownloadView(PDFReportView):
    def get(self, request, *args, **kwargs):
        user = request.user
        logger.info(f"User {user.username} initiated a report download.")
        pdf = self.generate_pdf()
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="{user.username}-report.pdf"'
        )
        response.write(pdf)
        log_user_activity(request, user, "assessment report downloaded")
        logger.info(f"User {user.username} successfully downloaded the report.")
        return response


pdfreportdownload = PDFReportDownloadView.as_view()


class PDFReportPrintView(PDFReportView):
    def get(self, request, *args, **kwargs):
        user = request.user
        logger.info(f"User {user.username} initiated a report print.")
        pdf = self.generate_pdf()
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = (
            f'inline; filename="{user.username}-report.pdf"'
        )
        response.write(pdf)
        log_user_activity(request, user, "assessment report printed")
        logger.info(f"User {user.username} successfully printed the report.")
        return response


pdfreportprint = PDFReportPrintView.as_view()


class PendingResultView(ActiveUserRequiredMixin, FilterView):
    require_non_staff = True
    filterset_class = QuestionnaireResponseFilter
    model = QuestionnaireResponse
    template_name = "patients/pending-results.html"
    context_object_name = "items"
    ordering = ["-submission_date", "-updated_date"]
    paginate_by = 9

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(state=STATE.IN_PROGRESS, user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title_root"] = "Results In Progress"
        log_user_activity(
            self.request, self.request.user, "viewed uncompleted assessment"
        )
        logger.info(
            f"User {self.request.user.username} viewed uncompleted assessments."
        )

        return context


pending_result = PendingResultView.as_view()


class PendingResultDeleteView(ActiveUserRequiredMixin, View):
    require_non_staff = True

    def post(self, request, *args, **kwargs):
        try:
            result_id = request.POST.get("result_id")
            result = get_object_or_404(QuestionnaireResponse, id=result_id)
            result.delete()
            log_user_activity(self.request, request.user, "deleted pending result")
            messages.success(request, "Resulte deleted successfully.")
            return JsonResponse(
                {"success": True, "message": "Result deleted successfully."}
            )
        except Exception as e:
            logger.error(
                f"User {request.user.username} failed to delete result {result_id}. Error: {str(e)}"
            )
            messages.error(request, "Unable to delete result.")
            return JsonResponse(
                {"success": False, "message": "Resulte unable to delete!"}
            )


pending_result_delete = PendingResultDeleteView.as_view()


class PredictionResultView(ActiveUserRequiredMixin, FilterView):
    allow_both = True
    filterset_class = PredictionResultFilter
    model = PredictionResult
    template_name = "patients/result-histores.html"
    context_object_name = "results"
    ordering = ["-submission_date", "-timestamp"]
    paginate_by = 9

    def get_queryset(self):
        query = super().get_queryset()
        return query.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title_root"] = "Prediction Results"
        log_user_activity(self.request, self.request.user, "viewed all reports")
        logger.info(f"User {self.request.user.username} viewed all reports.")

        return context


result_hostores = PredictionResultView.as_view()


class PredictionResultDeleteView(ActiveUserRequiredMixin, View):
    require_non_staff = True

    def post(self, request, *args, **kwargs):
        try:
            result_id = request.POST.get("result_id")
            result = get_object_or_404(PredictionResult, id=result_id)
            result.deleted = True
            result.save()
            log_user_activity(
                self.request, self.request.user, "deleted assessment result"
            )
            messages.success(request, "Resulte deleted successfully.")
            return JsonResponse(
                {"success": True, "message": "Result deleted successfully."}
            )
        except Exception as e:
            logger.error(
                f"User {request.user.username} failed to delete result {result_id}. Error: {str(e)}"
            )
            messages.error(request, "Unable to delete result.")
            return JsonResponse(
                {"success": False, "message": "Resulte unable to delete!"}
            )


resultdelete_view = PredictionResultDeleteView.as_view()


class FeedbackView(ActiveUserRequiredMixin, View):
    require_non_staff = True

    def post(self, request, *args, **kwargs):
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.save()
            log_user_activity(request, request.user, "provided feedback")
            return JsonResponse(
                {"success": True, "message": "Thank you for your feedback!"}
            )
        else:
            logger.error(
                f"User {request.user.username} failed to submit feedback. Errors: {form.errors}"
            )
            return JsonResponse({"success": False, "errors": form.errors})


feedback = FeedbackView.as_view()


class ContactView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "contact.html", {"title_root": "Contact"})

    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_message = form.save(commit=False)
            if request.user.is_authenticated:
                contact_message.user = request.user
            contact_message.save()
            log_user_activity(request, request.user, "contacted administration")
            return JsonResponse(
                {"success": True, "message": "Thank you for your message!"}
            )
        else:
            return JsonResponse({"success": False, "errors": form.errors})


contactview = ContactView.as_view()


class AboutView(View):
    template_name = "about.html"

    def get(self, request, *args, **kwargs):
        log_user_activity(request, request.user, "viewed about page")
        return render(request, self.template_name, self.get_context())

    def get_context(self):
        context = {
            "title_root": "About Us",
        }
        return context


about = AboutView.as_view()


class FAQView(TemplateView):
    template_name = "faqs.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["faqs"] = FAQS
        context["title_root"] = "FAQs"
        log_user_activity(self.request, self.request.user, "viewed faqs page")
        return context

    def get(self, request, *args, **kwargs):
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            query = request.GET.get("q", "").lower()
            filtered_faqs = []

            for section in FAQS:
                filtered_questions = [
                    question
                    for question in section["questions"]
                    if query in question["question"].lower()
                    or query in question["answer"].lower()
                ]
                if filtered_questions:
                    filtered_faqs.append(
                        {"heading": section["heading"], "questions": filtered_questions}
                    )

            return JsonResponse(filtered_faqs, safe=False)

        return super().get(request, *args, **kwargs)


faqs = FAQView.as_view()


class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title_root"] = "Home"
        log_user_activity(self.request, self.request.user, "viewed home page")
        return context


homeview = HomeView.as_view()


class Error500View(TemplateView):
    template_name = "errors/500.html"
    extra_context = {"error_code": 500, "title_root": "Internal Server Error"}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["request_path"] = self.request.path
        context["user"] = self.request.user
        return context

    def dispatch(self, request, *args, **kwargs):
        user = request.user if request.user.is_authenticated else None
        log_user_activity(request, user, "500 Internal Server Error encountered")
        logger.error(f"500 error at {request.path}")
        return super().dispatch(request, *args, **kwargs)


error500view = Error500View.as_view()


class Error403View(TemplateView):
    template_name = "errors/403.html"
    extra_context = {"error_code": 403, "title_root": "Forbidden"}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["request_path"] = self.request.path
        context["user"] = self.request.user
        return context

    def dispatch(self, request, *args, **kwargs):
        user = request.user if request.user.is_authenticated else None
        log_user_activity(request, user, "403 Forbidden error encountered")
        logger.warning(f"403 Forbidden error at {request.path}")
        return super().dispatch(request, *args, **kwargs)


error403view = Error403View.as_view()


class Error404View(TemplateView):
    template_name = "errors/404.html"
    extra_context = {"error_code": 404, "title_root": "Page Not Found"}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["request_path"] = self.request.path
        context["user"] = self.request.user
        return context

    def dispatch(self, request, *args, **kwargs):
        user = request.user if request.user.is_authenticated else None
        log_user_activity(request, user, "404 Not Found error encountered")
        logger.info(f"404 Not Found error at {request.path}")
        return super().dispatch(request, *args, **kwargs)


error404view = Error404View.as_view()


class Error400View(TemplateView):
    template_name = "errors/400.html"
    extra_context = {"error_code": 400, "title_root": "Bad Request"}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["request_path"] = self.request.path
        context["user"] = self.request.user
        return context

    def dispatch(self, request, *args, **kwargs):
        user = request.user if request.user.is_authenticated else None
        log_user_activity(request, user, "400 Bad Request error encountered")
        logger.warning(f"400 Bad Request error at {request.path}")
        return super().dispatch(request, *args, **kwargs)


error400view = Error400View.as_view()
