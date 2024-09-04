import re
from django.http import Http404, JsonResponse, HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from PaulVideoPlatform.utils import MailUtils
from accounts.filters import AccountFilter
from accounts.forms import UserCreateForm
from accounts.mixins import ActiveUserRequiredMixin
from accounts.models import Account
from accounts.templatetags.custom_filters import calculate_age
from ml.utils import DecimalEncoder, log_user_activity
from patients.filters import (
    ActivityLogFilter,
    ContactFilter,
    FeedbackFilterFilter,
    QuestionnaireResponseFilter,
    TrainedModelFilterFilter,
)
from patients.models import (
    STATE,
    Contact,
    Feedback,
    PredictionResult,
    QuestionnaireResponse,
)
from patients.utils import (
    FEATURE_ABBRI,
    FEATURE_EXPLANATIONS,
    PROBABILITY_SUMMARIES,
    RATE_CHOICES,
    SLIDER_LABELS,
    HelpResponse,
)
from .models import ActivityLog, EmailSettings, GeneralSettings, TrainedModel
from .filters import PredictionResultFilter
from django.db.models import Avg, Q, Count, F
from django.db.models.functions import TruncMonth, TruncWeek
from datetime import date
from django.db.models.functions import ExtractWeekDay
from collections import defaultdict
import json
from django_filters.views import FilterView
from django.contrib import messages
from django.views.generic import DetailView
from django.views.generic.edit import UpdateView
from .forms import EmailSettingsForm, GeneralSettingsForm
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import logging
from django.shortcuts import get_object_or_404
from django.views.generic import View
from io import BytesIO
import base64
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Table,
    TableStyle,
    Spacer,
    Image,
)
from django.views.generic import TemplateView
from django.core.paginator import Paginator
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from collections import defaultdict
from datetime import date

logger = logging.getLogger("custom_logger")

from django.views import View
from django.utils import timezone
from django.db.models import Count
from django.shortcuts import render
from django.db.models.functions import TruncMonth, ExtractWeekDay


class DashboardView(ActiveUserRequiredMixin, View):
    require_staff = True
    template_name = "ml/dashboard.html"

    def get_chart_data(self, queryset, date_field, group_by="month"):
        if group_by == "month":
            # Initialize the months
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
            counts = [0] * 12  # Initialize counts to zero for all months

            # Get data from the queryset
            data = (
                queryset.annotate(month=TruncMonth(date_field))
                .values("month")
                .annotate(count=Count("id"))
                .order_by("month")
            )

            # Populate counts based on the available data
            for entry in data:
                month_idx = (
                    entry["month"].month - 1
                )  # Convert month to zero-based index
                counts[month_idx] = entry["count"]

            labels = months

        elif group_by == "weekday":
            data = (
                queryset.annotate(weekday=ExtractWeekDay(date_field))
                .values("weekday")
                .annotate(count=Count("id"))
                .order_by("weekday")
            )
            labels = [
                "Sunday",
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
            ]
            counts = [0] * 7
            for entry in data:
                counts[entry["weekday"] - 1] = entry["count"]

        return {"labels": labels, "data": counts}

    def get(self, request, *args, **kwargs):
        # General statistics
        total_users = Account.objects.count()
        active_users = Account.objects.filter(is_active=True).count()
        total_assessments = PredictionResult.objects.count()

        one_month_ago = timezone.now() - timezone.timedelta(days=30)
        recent_signups = Account.objects.filter(date_joined__gte=one_month_ago).count()

        # Preparing chart data
        user_chart_data = self.get_chart_data(Account.objects.all(), "date_joined")
        active_users_chart_data = self.get_chart_data(
            Account.objects.filter(is_active=True), "date_joined"
        )
        assessments_chart_data = self.get_chart_data(
            PredictionResult.objects.all(), "submission_date"
        )
        signups_chart_data = self.get_chart_data(
            Account.objects.filter(date_joined__gte=one_month_ago),
            "date_joined",
            group_by="weekday",
        )

        recent_activities = ActivityLog.objects.exclude(user=request.user).order_by(
            "-timestamp"
        )[:5]

        context = {
            "total_users": total_users,
            "active_users": active_users,
            "recent_signups": recent_signups,
            "total_assessments": total_assessments,
            "recent_activities": recent_activities,
            "title_root": "Dashboard",
            "user_chart_data": user_chart_data,
            "active_users_chart_data": active_users_chart_data,
            "assessments_chart_data": assessments_chart_data,
            "signups_chart_data": signups_chart_data,
        }

        return render(request, self.template_name, context)


class DataVisualizationView(View):
    template_name = "ml/data_visualization.html"
    context_object_name = "results"

    def get(self, request, *args, **kwargs):
        logger.info(f"User '{request.user.username}' accessed data visualization page.")
        log_user_activity(request, request.user, "accessed data visualization")

        if self.is_ajax(request):
            # Return initial data as JSON for AJAX requests
            return JsonResponse(
                self.get_chart_data(PredictionResult.objects.all()), safe=False
            )

        # Render the initial page without filtering
        return self.render_page(request)

    def post(self, request, *args, **kwargs):

        logger.info(
            f"User '{request.user.username}' applied filters on data visualization."
        )
        log_user_activity(
            request, request.user, "applied filters on data visualization"
        )

        if self.is_ajax(request):
            filterset = PredictionResultFilter(
                request.POST or None, queryset=PredictionResult.objects.all()
            )

            if filterset.is_valid():
                queryset = filterset.qs
            else:
                queryset = PredictionResult.objects.all()

            # Return updated chart data as JSON
            return JsonResponse(self.get_chart_data(queryset), safe=False)

        # Apply filters based on POST data

        return self.render_page(request, apply_filters=True)

    def render_page(self, request, apply_filters=False):
        # Initialize the filterset with POST data if applicable
        filterset = PredictionResultFilter(
            request.POST or None, queryset=PredictionResult.objects.all()
        )

        # Check if we need to apply filters and if the filterset is valid
        if apply_filters and filterset.is_valid():
            queryset = filterset.qs
        else:
            # If not applying filters or the filterset is invalid, use all results
            queryset = PredictionResult.objects.all()

        context = {
            "title_root": "Data Visualization",
            "filter": filterset,
            **self.get_chart_data(queryset),
        }

        # Render the page with the context
        return render(request, self.template_name, context)

    def get_chart_data(self, queryset):
        # Prepare the chart data
        return {
            "pie_chart_html": self.prepare_pie_chart(queryset),
            "bar_chart_html": self.prepare_bar_chart_data(queryset),
            "radar_chart_html": self.prepare_radar_chart_data(queryset),
            "histogram_chart_html": self.prepare_histogram_data(queryset),
            "mixed_chart_html": self.prepare_mixed_chart_data(queryset),
            "area_chart_html": self.prepare_area_chart_data(queryset),
            "line_chart_html": self.prepare_line_chart_data(queryset),
        }

    def is_ajax(self, request):
        """Check if the request is an AJAX request."""
        return (
            request.headers.get("x-requested-with") == "XMLHttpRequest"
            or request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest"
        )

    def prepare_pie_chart(self, queryset):
        # Prepare advanced pie chart with Plotly
        pie_chart_data = {"labels": [], "series": []}

        for result in queryset:
            risk_level = result.risk_level
            print("Result: ", result)
            if risk_level not in pie_chart_data["labels"]:
                pie_chart_data["labels"].append(risk_level)
                pie_chart_data["series"].append(0)
            pie_chart_data["series"][pie_chart_data["labels"].index(risk_level)] += 1

        fig = go.Figure(
            data=[
                go.Pie(
                    labels=pie_chart_data["labels"],
                    values=pie_chart_data["series"],
                    hole=0.4,
                    hoverinfo="label+percent",
                    textinfo="value",
                )
            ]
        )

        fig.update_layout(
            title="Distribution of Risk Levels",
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5,
            ),
            margin=dict(l=20, r=20, t=40, b=20),
        )

        config = {
            "displaylogo": False,
            "modeBarButtonsToRemove": [
                "zoom2d",
                "select2d",
                "lasso2d",
                "hoverCompareCartesian",
                "hoverClosestCartesian",
            ],
            "displayModeBar": True,
        }

        return fig.to_html(
            config=config, include_plotlyjs=True, full_html=False, div_id="pieChart"
        )

    def prepare_bar_chart_data(self, queryset=None):
        if queryset is None:
            queryset = self.object_list

        # Initialize dictionaries for grouping by year and age group
        year_age_groups = defaultdict(lambda: defaultdict(list))
        today = date.today()

        for record in queryset:
            # Ensure that record.submission_date and record.user.date_of_birth are not None
            if record.submission_date and record.user.date_of_birth:
                # Calculate the year of the record and the age of the user
                record_year = record.submission_date.year
                date_of_birth = record.user.date_of_birth
                age = (
                    today.year
                    - date_of_birth.year
                    - (
                        (today.month, today.day)
                        < (date_of_birth.month, date_of_birth.day)
                    )
                )

                # Determine the age group
                if age < 20:
                    age_group = "Under 20"
                elif 20 <= age < 30:
                    age_group = "20-29"
                elif 30 <= age < 40:
                    age_group = "30-39"
                elif 40 <= age < 50:
                    age_group = "40-49"
                elif 50 <= age < 60:
                    age_group = "50-59"
                else:
                    age_group = "60+"

                # Append the risk score to the appropriate year and age group
                risk_score = (
                    round(record.risk_score, 2) if record.risk_score is not None else 0
                )
                year_age_groups[record_year][age_group].append(risk_score)

        # Prepare data for the bar chart
        bar_chart_data = {"categories": [], "series": []}
        series_data = defaultdict(list)

        for year, age_groups in year_age_groups.items():
            for age_group, risk_scores in age_groups.items():
                category_label = f"{year} ({age_group})"
                bar_chart_data["categories"].append(category_label)

                # Calculate statistical measures: min, max, and average
                if risk_scores:  # Ensure there are risk scores to calculate statistics
                    min_risk = min(risk_scores)
                    max_risk = max(risk_scores)
                    avg_risk = sum(risk_scores) / len(risk_scores)

                    series_data["Min Risk"].append(round(min_risk, 2))
                    series_data["Max Risk"].append(round(max_risk, 2))
                    series_data["Avg Risk"].append(round(avg_risk, 2))
                else:
                    series_data["Min Risk"].append(0)
                    series_data["Max Risk"].append(0)
                    series_data["Avg Risk"].append(0)

        # Create the Plotly bar chart
        fig = go.Figure()

        colors = {"Min Risk": "blue", "Max Risk": "red", "Avg Risk": "green"}

        for stat, data in series_data.items():
            fig.add_trace(
                go.Bar(
                    x=bar_chart_data["categories"],
                    y=data,
                    name=stat,
                    marker_color=colors[stat],
                    text=data,
                    textposition="auto",
                )
            )

        # Customize the layout to enhance aesthetics
        fig.update_layout(
            title={
                "text": "Risk Score Analysis by Year and Age Group",
                "font_size": 22,
                "xanchor": "center",
                "x": 0.5,
            },
            xaxis_title="Year and Age Group",
            yaxis_title="Risk Score",
            barmode="group",
            xaxis=dict(
                tickangle=-45,
                tickvals=list(range(len(bar_chart_data["categories"]))),
                ticktext=bar_chart_data["categories"],
            ),
            legend=dict(
                title="Risk Statistics",
                orientation="h",
                x=0.5,
                xanchor="center",
                y=-0.2,
                yanchor="top",
                bgcolor="rgba(255, 255, 255, 0.7)",
                borderwidth=1,
                font=dict(size=13),
            ),
            autosize=True,
        )

        config = {
            "displaylogo": False,
            "modeBarButtonsToRemove": [
                "zoom2d",
                "select2d",
                "lasso2d",
                "hoverCompareCartesian",
                "hoverClosestCartesian",
            ],
            "displayModeBar": True,
        }

        return fig.to_html(
            config=config, include_plotlyjs=True, full_html=False, div_id="barChart"
        )

    def prepare_radar_chart_data(self, queryset):
        labels = ["Risk Level: Low", "Risk Level: Moderate", "Risk Level: High"]

        benign_data = []
        malignant_data = []

        for label in labels:
            if "Low" in label:
                benign_data.append(
                    queryset.filter(
                        risk_level="Low", probability_benign__gte=0.5
                    ).count()
                )
                malignant_data.append(
                    queryset.filter(
                        risk_level="Low", probability_malignant__gte=0.5
                    ).count()
                )
            elif "Moderate" in label:
                benign_data.append(
                    queryset.filter(
                        risk_level="Moderate", probability_benign__gte=0.5
                    ).count()
                )
                malignant_data.append(
                    queryset.filter(
                        risk_level="Moderate", probability_malignant__gte=0.5
                    ).count()
                )
            elif "High" in label:
                benign_data.append(
                    queryset.filter(
                        risk_level="High", probability_benign__gte=0.5
                    ).count()
                )
                malignant_data.append(
                    queryset.filter(
                        risk_level="High", probability_malignant__gte=0.5
                    ).count()
                )

        # Create radar chart
        fig = go.Figure()

        # Add trace for benign cases
        fig.add_trace(
            go.Scatterpolar(
                r=benign_data,
                theta=labels,
                fill="toself",
                name="Benign Cases",
                line=dict(color="royalblue"),
                fillcolor="rgba(66, 133, 244, 0.2)",
            )
        )

        # Add trace for malignant cases
        fig.add_trace(
            go.Scatterpolar(
                r=malignant_data,
                theta=labels,
                fill="toself",
                name="Malignant Cases",
                line=dict(color="firebrick"),
                fillcolor="rgba(203, 32, 39, 0.2)",
            )
        )

        # Customize the layout for better aesthetics
        fig.update_layout(
            title={
                "text": "Risk Level Distribution by Case Type",
                "font_size": 24,
                "x": 0.5,
                "xanchor": "center",
            },
            polar=dict(
                angularaxis=dict(
                    gridcolor="lightgray", tickfont=dict(size=12), showline=True
                ),
                radialaxis=dict(
                    visible=True,
                    range=[0, max(max(benign_data), max(malignant_data)) + 5],
                ),
            ),
            showlegend=True,
            legend=dict(
                title="Case Type", orientation="h", x=0.5, xanchor="center", y=-0.1
            ),
            autosize=True,
        )

        # Return the figure as HTML
        config = {
            "displaylogo": False,
            "modeBarButtonsToRemove": [
                "zoom2d",
                "select2d",
                "lasso2d",
                "hoverCompareCartesian",
                "hoverClosestCartesian",
            ],
            "displayModeBar": True,
        }

        return fig.to_html(
            config=config, include_plotlyjs=True, full_html=False, div_id="radarChart"
        )

    def prepare_histogram_data(self, queryset):
        # Prepare data for the age distribution histogram
        today = date.today()
        age_distribution = defaultdict(int)

        for record in queryset:
            date_of_birth = record.user.date_of_birth
            if date_of_birth is not None:
                age = (
                    today.year
                    - date_of_birth.year
                    - (
                        (today.month, today.day)
                        < (date_of_birth.month, date_of_birth.day)
                    )
                )
                age_distribution[age] += 1

        if not age_distribution:
            return {"labels": [], "series": []}

        # Calculate bin size dynamically
        ages = list(age_distribution.keys())
        min_age, max_age = min(ages), max(ages)
        bin_size = max(1, (max_age - min_age) // 10)  # Adjust bin size based on range

        # Define age bins
        bins = list(range(min_age, max_age + bin_size, bin_size))
        binned_data = defaultdict(int)

        for age, count in age_distribution.items():
            bin_index = (age // bin_size) * bin_size
            binned_data[bin_index] += count

        sorted_bins = sorted(binned_data.keys())
        bin_counts = [binned_data[bin] for bin in sorted_bins]

        # Create histogram plotly chart
        fig = go.Figure()

        fig.add_trace(
            go.Histogram(
                x=[age for age in age_distribution.keys()],
                name="Age Distribution",
                xbins=dict(start=min_age, end=max_age, size=bin_size),
                marker_color="royalblue",
                opacity=0.7,
            )
        )

        # Add mean and median lines
        if ages:
            mean_age = sum(ages) / len(ages)
            median_age = sorted(ages)[len(ages) // 2]

            fig.add_vline(
                x=mean_age,
                line_dash="dash",
                line_color="orange",
                annotation_text=f"Mean Age: {mean_age:.2f}",
                annotation_position="top right",
                annotation_font_size=12,
            )

            fig.add_vline(
                x=median_age,
                line_dash="dot",
                line_color="red",
                annotation_text=f"Median Age: {median_age:.2f}",
                annotation_position="top right",
                annotation_font_size=12,
            )

        # Customize the layout
        fig.update_layout(
            title={
                "text": "Age Distribution of Records",
                "font_size": 24,
                "x": 0.5,
                "xanchor": "center",
            },
            xaxis=dict(
                title="Age", tickmode="linear", dtick=bin_size, gridcolor="lightgray"
            ),
            yaxis=dict(title="Count", gridcolor="lightgray"),
            bargap=0.2,
            showlegend=True,
            legend=dict(
                title="Legend", orientation="h", x=0.5, xanchor="center", y=-0.1
            ),
            autosize=True,
        )

        # Return the figure as HTML
        config = {
            "displaylogo": False,
            "modeBarButtonsToRemove": [
                "zoom2d",
                "select2d",
                "lasso2d",
                "hoverCompareCartesian",
                "hoverClosestCartesian",
            ],
            "displayModeBar": True,
        }

        return fig.to_html(
            config=config,
            include_plotlyjs=True,
            full_html=False,
            div_id="histogramChart",
        )

    def prepare_mixed_chart_data(self, queryset=None):
        if queryset is None:
            queryset = self.object_list

        mixed_chart_data = {"categories": [], "mean": [], "worst": [], "standard": []}

        # Initialize lists for mean, worst, and standard
        mean_series = [0] * 10
        worst_series = [0] * 10
        standard_series = [0] * 10

        # Counter to track the number of records
        record_count = 0

        for record in queryset:
            chart_data = getattr(record, "chart_data", None)  # Safely get chart_data

            if chart_data is not None and isinstance(chart_data, dict):
                # Ensure that chart_data has the required fields
                if all(
                    key in chart_data
                    for key in ("mean", "worst", "standard", "categories")
                ):
                    record_count += 1
                    mean_series = [
                        x + y for x, y in zip(mean_series, chart_data["mean"])
                    ]
                    worst_series = [
                        x + y for x, y in zip(worst_series, chart_data["worst"])
                    ]
                    standard_series = [
                        x + y for x, y in zip(standard_series, chart_data["standard"])
                    ]

                    if not mixed_chart_data["categories"]:
                        mixed_chart_data["categories"] = chart_data["categories"]
                else:
                    print(f"Missing required fields in chart_data: {chart_data}")
            else:
                print(f"Invalid chart_data format or None: {chart_data}")

        # Average the values across all records
        if record_count > 0:
            mean_series = [round(x / record_count, 2) for x in mean_series]
            worst_series = [round(x / record_count, 2) for x in worst_series]
            standard_series = [round(x / record_count, 2) for x in standard_series]

        # Assign the lists to mixed_chart_data
        mixed_chart_data["mean"] = mean_series
        mixed_chart_data["worst"] = worst_series
        mixed_chart_data["standard"] = standard_series

        # Create the Plotly mixed chart
        fig = go.Figure()

        # Add traces for Mean, Worst, and Standard data
        fig.add_trace(
            go.Scatter(
                x=mixed_chart_data["categories"],
                y=mixed_chart_data["mean"],
                mode="lines+markers",
                name="Mean",
                line=dict(color="royalblue", width=2),
                marker=dict(size=8, symbol="circle", color="royalblue"),
            )
        )

        fig.add_trace(
            go.Scatter(
                x=mixed_chart_data["categories"],
                y=mixed_chart_data["worst"],
                mode="lines+markers",
                name="Worst",
                line=dict(color="firebrick", width=2),
                marker=dict(size=8, symbol="square", color="firebrick"),
            )
        )

        fig.add_trace(
            go.Scatter(
                x=mixed_chart_data["categories"],
                y=mixed_chart_data["standard"],
                mode="lines+markers",
                name="Standard",
                line=dict(color="darkorange", width=2),
                marker=dict(size=8, symbol="diamond", color="darkorange"),
            )
        )

        # Customize the layout
        fig.update_layout(
            title={
                "text": "Mixed Chart of Mean, Worst, and Standard Values",
                "font_size": 24,
                "x": 0.5,
                "xanchor": "center",
            },
            xaxis=dict(
                title="Categories",
                tickangle=-45,
                title_font_size=16,
                tickfont_size=14,
                gridcolor="lightgray",
            ),
            yaxis=dict(
                title="Values",
                title_font_size=16,
                tickfont_size=14,
                gridcolor="lightgray",
            ),
            legend=dict(
                title="Legend", orientation="h", x=0.5, xanchor="center", y=-0.1
            ),
            autosize=True,
        )

        # Return the figure as HTML
        config = {
            "displaylogo": False,
            "modeBarButtonsToRemove": [
                "zoom2d",
                "select2d",
                "lasso2d",
                "hoverCompareCartesian",
                "hoverClosestCartesian",
            ],
            "displayModeBar": True,
        }

        return fig.to_html(
            config=config, include_plotlyjs=True, full_html=False, div_id="mixedChart"
        )

    def prepare_area_chart_data(self, queryset=None):
        if queryset is None:
            queryset = self.object_list  # Default to the filtered queryset

        # Initialize data structure
        area_chart_data = {"categories": [], "series": []}

        # Create series data for Low, Moderate, and High risk levels
        series_data = {
            "Low": [],
            "Moderate": [],
            "High": [],
        }

        # Aggregate data by day and risk level
        datewise_data = (
            queryset.values("submission_date")
            .annotate(
                low_risk_count=Count("id", filter=Q(risk_level="Low")),
                medium_risk_count=Count("id", filter=Q(risk_level="Moderate")),
                high_risk_count=Count("id", filter=Q(risk_level="High")),
            )
            .order_by("submission_date")
        )

        # Populate categories and series
        for entry in datewise_data:
            area_chart_data["categories"].append(
                entry["submission_date"].strftime("%Y-%m-%d")
            )
            series_data["Low"].append(entry["low_risk_count"])
            series_data["Moderate"].append(entry["medium_risk_count"])
            series_data["High"].append(entry["high_risk_count"])

        # Create the Plotly area chart
        fig = go.Figure()

        # Add traces for each risk level
        fig.add_trace(
            go.Scatter(
                x=area_chart_data["categories"],
                y=series_data["Low"],
                mode="lines",
                fill="tozeroy",
                name="Low Risk",
                line=dict(color="blue", width=2),
                fillcolor="rgba(0, 0, 255, 0.3)",
            )
        )

        fig.add_trace(
            go.Scatter(
                x=area_chart_data["categories"],
                y=series_data["Moderate"],
                mode="lines",
                fill="tonexty",
                name="Moderate Risk",
                line=dict(color="orange", width=2),
                fillcolor="rgba(255, 165, 0, 0.3)",
            )
        )

        fig.add_trace(
            go.Scatter(
                x=area_chart_data["categories"],
                y=series_data["High"],
                mode="lines",
                fill="tonexty",
                name="High Risk",
                line=dict(color="red", width=2),
                fillcolor="rgba(255, 0, 0, 0.3)",
            )
        )

        # Customize the layout
        fig.update_layout(
            title={
                "text": "Risk Level Distribution Over Time",
                "font_size": 24,
                "x": 0.5,
                "xanchor": "center",
            },
            xaxis=dict(
                title="Submission Date",
                title_font_size=16,
                tickfont_size=14,
                gridcolor="lightgray",
            ),
            yaxis=dict(
                title="Number of Cases",
                title_font_size=16,
                tickfont_size=14,
                gridcolor="lightgray",
            ),
            legend=dict(
                title="Risk Levels", orientation="h", x=0.5, xanchor="center", y=-0.1
            ),
            autosize=True,
            template="plotly_white",  # Provides a clean white background
        )

        # Return the figure as HTML
        config = {
            "displaylogo": False,
            "modeBarButtonsToRemove": [
                "zoom2d",
                "select2d",
                "lasso2d",
                "hoverCompareCartesian",
                "hoverClosestCartesian",
            ],
            "displayModeBar": True,
        }

        return fig.to_html(
            config=config, include_plotlyjs=True, full_html=False, div_id="areaChart"
        )

    def prepare_line_chart_data(self, queryset):
        # Group data by the day of the week and calculate the average risk score
        weekday_data = (
            queryset.annotate(weekday=ExtractWeekDay("submission_date"))
            .values("weekday")
            .annotate(avg_risk_score=Avg("risk_score"))
            .order_by("weekday")
        )

        # Weekday mapping (1=Sunday, 2=Monday, ..., 7=Saturday)
        weekday_mapping = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

        # Prepare the data for the line chart
        categories = []
        series = []
        for entry in weekday_data:
            weekday = entry["weekday"]
            categories.append(weekday_mapping[weekday - 1])
            series.append(float(entry["avg_risk_score"]))

        # Create Plotly line chart
        fig = go.Figure()

        # Add line trace
        fig.add_trace(
            go.Scatter(
                x=categories,
                y=series,
                mode="lines+markers",
                name="Average Risk Score",
                line=dict(color="royalblue", width=3, dash="solid"),
                marker=dict(
                    size=8,
                    color="royalblue",
                    line=dict(width=2, color="rgba(0, 0, 0, 0.5)"),
                ),
                text=series,
                textposition="top center",
                hoverinfo="x+y",
            )
        )

        # Update layout for better aesthetics
        fig.update_layout(
            title={
                "text": "Average Risk Score by Day of the Week",
                "font_size": 24,
                "xanchor": "center",
                "x": 0.5,
            },
            xaxis_title="Day of the Week",
            yaxis_title="Average Risk Score",
            xaxis=dict(
                tickangle=-45,
                showline=True,
                showgrid=False,
                linecolor="black",
                linewidth=1,
                gridcolor="lightgray",
            ),
            yaxis=dict(
                showline=True,
                showgrid=True,
                linecolor="black",
                linewidth=1,
                gridcolor="lightgray",
            ),
            plot_bgcolor="white",
            paper_bgcolor="rgba(255, 255, 255, 0.8)",
            margin=dict(l=40, r=40, t=40, b=40),
            font=dict(size=12, color="black"),
            legend=dict(
                title="Legend",
                orientation="h",
                x=0.5,
                xanchor="center",
                y=-0.15,
                yanchor="top",
                bgcolor="rgba(255, 255, 255, 0.8)",
                borderwidth=1,
                font=dict(size=12),
            ),
            hovermode="closest",
        )

        config = {
            "displaylogo": False,
            "modeBarButtonsToRemove": [
                "zoom2d",
                "select2d",
                "lasso2d",
                "hoverCompareCartesian",
                "hoverClosestCartesian",
            ],
            "displayModeBar": True,
        }

        return fig.to_html(
            config=config, include_plotlyjs=True, full_html=False, div_id="lineChart"
        )


class RecordManagementView(ActiveUserRequiredMixin, FilterView):
    require_staff = True
    filterset_class = QuestionnaireResponseFilter
    model = QuestionnaireResponse
    template_name = "ml/record_management.html"
    context_object_name = "items"
    ordering = ["-submission_date", "-updated_date"]
    paginate_by = 9

    def get(self, request, *args, **kwargs):
        logger.info(f"User '{request.user.username}' accessed record management page.")
        log_user_activity(request, request.user, "accessed record management")
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        logger.info("Record management view accessed.")
        context["title_root"] = "Record Management"
        return context


class UserManagementView(ActiveUserRequiredMixin, FilterView):
    require_staff = True
    model = Account
    template_name = "ml/user_list.html"
    context_object_name = "users"
    filterset_class = AccountFilter
    paginate_by = 10
    ordering = ["-date_joined"]

    def get(self, request, *args, **kwargs):
        logger.info(f"User '{request.user.username}' accessed user management page.")
        log_user_activity(request, request.user, "accessed user management")
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        query = super().get_queryset()
        logger.info("User management queryset filtered.")
        return query.exclude(pk=self.request.user.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title_root"] = "User Management"
        context["form"] = UserCreateForm()

        return context


class AddOrUpdateUserView(ActiveUserRequiredMixin, MailUtils, View):
    require_staff = True
    form_class = UserCreateForm

    def post(self, request, *args, **kwargs):
        user_id = request.POST.get("user_id")
        action = "updated" if user_id else "created"
        logger.info(f"User '{request.user.username}' initiated user {action} process.")

        if user_id:
            user = get_object_or_404(Account, id=user_id)
            form = self.form_class(request.POST, instance=user)
        else:
            form = self.form_class(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            if not user_id:
                user.set_password(Account.objects.make_random_password())
                user.is_active = False  # User needs to activate their account
            user.save()
            log_user_activity(request, request.user, f"{action} user '{user.email}'")
            logger.info(
                f"User '{user.email}' {action} successfully by '{request.user.username}'."
            )

            if not user.is_active:
                try:
                    self.compose_email(request, user)
                    logger.info(f"Activation email sent to '{user.email}'.")
                except Exception as e:
                    logger.error(
                        f"Failed to send activation email to '{user.email}': {e}",
                        exc_info=True,
                    )

            return JsonResponse(
                {"success": True, "message": f"User {action} successfully."}
            )
        else:
            errors = form.errors.as_json()
            logger.warning(
                f"User '{request.user.username}' failed to {action} user due to form errors: {errors}"
            )
            return JsonResponse({"success": False, "errors": errors}, status=400)


class UserDeleteView(ActiveUserRequiredMixin, View):
    require_staff = True

    def post(self, request, *args, **kwargs):
        user_id = request.POST.get("user_id")
        logger.info(
            f"User '{request.user.username}' initiated deletion of user ID '{user_id}'."
        )
        try:
            user = get_object_or_404(Account, id=user_id)
            user_email = user.email
            user.delete()
            log_user_activity(request, request.user, f"deleted user '{user_email}'")
            logger.info(
                f"User '{user_email}' deleted successfully by '{request.user.username}'."
            )
            return JsonResponse(
                {"success": True, "message": "User deleted successfully."}
            )
        except Account.DoesNotExist:
            logger.warning(f"User deletion failed: User ID '{user_id}' does not exist.")
            return JsonResponse(
                {"success": False, "message": "User does not exist."}, status=404
            )
        except Exception as e:
            logger.error(f"Error deleting user ID '{user_id}': {e}", exc_info=True)
            return JsonResponse(
                {"success": False, "message": "Error deleting user."}, status=500
            )


class GetUserView(ActiveUserRequiredMixin, View):
    require_staff = True

    def get(self, request, user_id, *args, **kwargs):
        try:
            user = get_object_or_404(Account, id=user_id)
            dob = user.date_of_birth
            data = {
                "id": user.id or "",
                "first_name": user.first_name or "N/A",
                "last_name": user.last_name or "N/A",
                "username": user.username or "N/A",
                "email": user.email or "N/A",
                "gender": user.gender or "N/A",
                "country": user.country or "N/A",
                "agree": user.agree if user.agree is not None else False,
                "dj": user.date_joined or "N/A",
                "ll": user.last_login or "N/A",
                "is_admin": user.is_admin if user.is_admin is not None else False,
                "usid": user.usid or "N/A",
                "date_of_birth": dob or "N/A",
                "dob": {
                    "year": dob.year if dob else "N/A",
                    "month": dob.month if dob else "N/A",
                    "day": dob.day if dob else "N/A",
                },
                "full_name": user.full_name() or "N/A",
                "created_by": user.created_by.username if user.created_by else "N/A",
            }
            logger.info(f"User {user_id} details retrieved successfully.")
            return JsonResponse(data)
        except Exception as e:
            logger.error(f"Error retrieving user {user_id}: {e}", exc_info=True)
            return JsonResponse({"error": "Contact not found."}, status=404)


class SendActivationEmailView(ActiveUserRequiredMixin, MailUtils, View):
    require_staff = True

    def post(self, request, *args, **kwargs):
        user_id = request.POST.get("user_id")
        user = get_object_or_404(Account, id=user_id)
        try:
            if not user.is_active:
                self.compose_email(request, user)
                msg = f"Activation link sent to {user.email}."
                logger.info(f"Activation email sent to {user.email}.")
                log_user_activity(
                    request, request.user, f"Activation email sent to {user.email}."
                )

            else:
                msg = f"User {user.username} is already active."
                logger.info(
                    f"Activation email not sent. User {user.username} is already active."
                )
            return JsonResponse({"success": True, "message": msg})
        except Exception as e:
            log_user_activity(
                request,
                request.user,
                f"Failed to send activation email to {user.email}: {e}",
                level="ERROR",
            )

            logger.error(
                f"SEND_ACTIVATION_EMAIL: Failed to send activation email to {user.email}: {e}",
                exc_info=True,
            )
            return JsonResponse(
                {"success": False, "message": "Error sending activation email."},
                status=500,
            )


class DeactivateAccountView(ActiveUserRequiredMixin, View):
    require_staff = True

    def post(self, request, user_id, *args, **kwargs):
        _user = request.user
        if not user_id:
            messages.error(request, "User ID is required.")
            logger.warning(
                f"DEACTIVATE ACCOUNT: User {user_id} account already deactivated."
            )
            log_user_activity(request, _user, "DEACTIVATE account, already deactivated")
        try:
            user = get_object_or_404(Account, id=user_id)
            if not user.is_active:
                messages.error(request, "User account is already deactivated.")
                logger.warning(
                    f"DEACTIVATE ACCOUNT: User {user_id} account already deactivated."
                )
                log_user_activity(
                    request, _user, "DEACTIVATE account, already deactivated"
                )
            else:
                user.is_active = False
                user.save()
                messages.success(request, "User account deactivated successfully.")
                log_user_activity(
                    request, _user, "DEACTIVATE account deactivated successfully."
                )
        except Account.DoesNotExist:
            messages.error(request, "User not found.")
            logger.error(f"DEACTIVATE_ACCOUNT: User {user_id} not found.")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            logger.error(f"DEACTIVATE_ACCOUNT: Error deactivating user {user_id}: {e}")

        return redirect("AdminHub:user-list")


class ContactListView(ActiveUserRequiredMixin, FilterView):
    require_staff = True
    model = Contact
    context_object_name = "contacts"
    template_name = "ml/contacts.html"
    filterset_class = ContactFilter
    paginate_by = 10
    ordering = ["-submitted_at"]

    def get(self, request, *args, **kwargs):
        logger.info("Contact list view accessed.")
        log_user_activity(request, request.user, "VIEW CONTACT LIST")
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title_root"] = "Contact List"
        return context


class ContactDetailView(ActiveUserRequiredMixin, View):
    require_staff = True

    def get(self, request, *args, **kwargs):
        contact_id = kwargs.get("pk")
        try:
            contact = Contact.objects.get(pk=contact_id)
            data = {
                "name": contact.name,
                "email": contact.email,
                "subject": contact.subject or "No Subject",
                "message": contact.message,
                "submitted_at": contact.submitted_at,
                "user": contact.user.username if contact.user else "Anonymous",
            }
            logger.info(
                f"VIEW_CONTACT_DETAIL: Contact details retrieved for ID {contact_id}."
            )
            log_user_activity(request, request.user, "VIEW CONTACT DETAIL")
            return JsonResponse(data)
        except Contact.DoesNotExist:
            logger.warning(f"Contact not found for ID {contact_id}.")
            return JsonResponse({"error": "Contact not found."}, status=404)


class DeleteContactsView(ActiveUserRequiredMixin, View):
    require_staff = True

    def post(self, request, *args, **kwargs):
        selected_ids = request.POST.getlist("selected_items")
        try:
            if selected_ids:
                contacts = Contact.objects.filter(id__in=selected_ids)
                count = contacts.count()
                contacts.delete()
                messages.success(request, f"{count} contact(s) deleted successfully.")
                log_user_activity(request, request.user, "DELETE CONTACTS")
                return JsonResponse({"success": True}, status=200)
            else:
                logger.warning(request, "DELETE_CONTACTS: No contacts selected.")
                return JsonResponse(
                    {"success": False, "error": "No contacts selected."}, status=400
                )
        except Exception as e:
            logger.error(
                request,
                "DELETE_CONTACTS",
                f"Error deleting contacts: {e}",
                level="ERROR",
            )
            return JsonResponse({"success": False, "error": str(e)}, status=400)


class ActivityLogListView(ActiveUserRequiredMixin, FilterView):
    require_staff = True
    model = ActivityLog
    context_object_name = "logs"
    template_name = "ml/logs.html"
    filterset_class = ActivityLogFilter
    paginate_by = 10
    ordering = ["-timestamp"]
    extra_context = {
        "title_root": "Activity Logs",
    }

    def get(self, request, *args, **kwargs):
        log_user_activity(request, request.user, "Activity log list view accessed.")
        return super().get(request, *args, **kwargs)


class LogDetailView(ActiveUserRequiredMixin, DetailView):
    require_staff = True
    model = ActivityLog
    template_name = "ml/log_detail.html"
    context_object_name = "log"

    def get_object(self, queryset=None):
        log_id = self.kwargs.get("pk")
        try:
            log = ActivityLog.objects.get(pk=log_id)
            log_user_activity(
                self.request,
                self.request.user,
                f"Successfully retrieved log with ID: {log_id}",
            )
            return log
        except ActivityLog.DoesNotExist:
            log_user_activity(
                self.request,
                self.request.user,
                f"VIEW LOG DETAIL: Log with ID {log_id} not found.",
                level="ERROR",
            )
            raise Http404("Log not found.")


class DeleteLogView(ActiveUserRequiredMixin, View):
    require_staff = True

    def post(self, request, *args, **kwargs):
        selected_ids = request.POST.getlist("selected_items")
        try:
            if selected_ids:
                log = ActivityLog.objects.filter(id__in=selected_ids)
                count = log.count()
                log.delete()
                messages.success(request, f"{count} log(s) deleted successfully.")
                log_user_activity(
                    request,
                    request.user,
                    f"DELETE_LOGS: {count} log(s) deleted: {selected_ids}",
                )
                return JsonResponse({"success": True}, status=200)
            else:
                log_user_activity(
                    request, "DELETE_LOGS" "No log selected for deletion."
                )
                return JsonResponse(
                    {"success": False, "error": "No log selected."}, status=400
                )
        except Exception as e:
            logger.error(request, "DELETE_LOGS Error deleting logs: {e}", level="ERROR")
            return JsonResponse({"success": False, "error": str(e)}, status=400)


class SystemSettingsView(ActiveUserRequiredMixin, UpdateView):
    require_staff = True
    template_name = "ml/system_settings.html"

    def get(self, request, *args, **kwargs):
        email_settings, _ = EmailSettings.objects.get_or_create(id=1)
        general_settings, _ = GeneralSettings.objects.get_or_create(id=1)

        email_form = EmailSettingsForm(instance=email_settings)
        general_form = GeneralSettingsForm(instance=general_settings)
        logger.info("System settings view accessed by user: %s", request.user.username)

        return render(
            request,
            self.template_name,
            {"email_form": email_form, "general_form": general_form},
        )

    def post(self, request, *args, **kwargs):
        email_settings, _ = EmailSettings.objects.get_or_create(id=1)
        general_settings, _ = GeneralSettings.objects.get_or_create(id=1)

        email_form = EmailSettingsForm(request.POST, instance=email_settings)
        general_form = GeneralSettingsForm(request.POST, instance=general_settings)

        if email_form.is_valid() and general_form.is_valid():
            email_form.save()
            general_form.save()
            logger.info("System settings updated successfully.")
            return JsonResponse(
                {"success": True, "message": "Settings updated successfully."}
            )
        else:
            errors = {
                "email_form_errors": email_form.errors,
                "general_form_errors": general_form.errors,
            }
            logger.error(f"Failed to update settings: {errors}")
            return JsonResponse({"success": False, "errors": errors})


class PredictionView(ActiveUserRequiredMixin, HelpResponse, View):
    require_staff = True
    template_name = "ml/measurement.html"

    def get_step_value(self, max_value):
        """
        Determine the step size based on the max_value.
        """
        if max_value <= 0.1:
            return 0.001
        else:
            return 0.01

    def add_sidebar(self):
        """
        Create sidebar sliders for user to input cell nuclei measurements.
        Returns:
            dict: User input values for the measurements.
        """
        # sidebar header "Cell Nuclei Measurements"
        data = self.get_clean_data()

        input_dict = {}
        sliders = []
        # Create sliders for each measurement and store user input in a dictionary
        for label, key in SLIDER_LABELS:
            max_value = float(data[key].max())
            value = float(data[key].mean())
            input_dict[key] = value
            step = self.get_step_value(max_value)
            sliders.append(
                {
                    "label": label,
                    "name": key,
                    "min": 0,
                    "max": max_value,
                    "from": value,
                    "step": step,
                }
            )
        return input_dict, sliders

    def get_radar_chart(self, input_data):
        """
        Generate a beautifully styled radar chart based on user input values.

        Args:
            input_data (dict): User input values for the measurements.

        Returns:
            plotly.graph_objects.Figure: Radar chart visualization.
        """
        input_data = self.get_scaled_values(input_data)

        categories = self.categories
        fig = go.Figure()

        # Add trace for mean values
        fig.add_trace(
            go.Scatterpolar(
                r=[
                    input_data["radius_mean"],
                    input_data["texture_mean"],
                    input_data["perimeter_mean"],
                    input_data["area_mean"],
                    input_data["smoothness_mean"],
                    input_data["compactness_mean"],
                    input_data["concavity_mean"],
                    input_data["concave points_mean"],
                    input_data["symmetry_mean"],
                    input_data["fractal_dimension_mean"],
                ],
                theta=categories,
                name="Mean Value",
                marker=dict(size=15, color="mediumseagreen", symbol="circle"),
                line=dict(color="mediumseagreen", width=1, dash="solid"),
            )
        )

        # Add trace for standard error values
        fig.add_trace(
            go.Scatterpolar(
                r=[
                    input_data["radius_se"],
                    input_data["texture_se"],
                    input_data["perimeter_se"],
                    input_data["area_se"],
                    input_data["smoothness_se"],
                    input_data["compactness_se"],
                    input_data["concavity_se"],
                    input_data["concave points_se"],
                    input_data["symmetry_se"],
                    input_data["fractal_dimension_se"],
                ],
                theta=categories,
                name="Standard Error",
                marker=dict(size=15, color="darkorange", symbol="diamond"),
                line=dict(color="darkorange", width=1, dash="dashdot"),
            )
        )

        # Add trace for worst values
        fig.add_trace(
            go.Scatterpolar(
                r=[
                    input_data["radius_worst"],
                    input_data["texture_worst"],
                    input_data["perimeter_worst"],
                    input_data["area_worst"],
                    input_data["smoothness_worst"],
                    input_data["compactness_worst"],
                    input_data["concavity_worst"],
                    input_data["concave points_worst"],
                    input_data["symmetry_worst"],
                    input_data["fractal_dimension_worst"],
                ],
                theta=categories,
                name="Worst Value",
                marker=dict(size=15, color="lightsalmon", symbol="square"),
                line=dict(color="lightsalmon", width=1, dash="dot"),
            )
        )

        # Customize the layout to enhance aesthetics
        fig.update_layout(
            title={
                "text": "Comprehensive Cell Nuclei Measurements",
                "font_size": 22,
                "xanchor": "center",
                "x": 0.5,
            },
            polar=dict(
                angularaxis=dict(
                    linewidth=2,
                    showline=True,
                    linecolor="black",
                    gridcolor="lightgray",
                ),
                radialaxis=dict(
                    side="counterclockwise",
                    showline=True,
                    linewidth=2,
                    gridcolor="white",
                    gridwidth=2,
                ),
            ),
            showlegend=False,
            legend=dict(
                title="Measurements",
                orientation="h",
                x=0.5,
                xanchor="center",
                y=-0.1,
                yanchor="top",
                bgcolor="rgba(255, 255, 255, 0.7)",
                borderwidth=1,
                font=dict(size=13),
            ),
            autosize=True,
        )

        config = {
            "displaylogo": False,
            "modeBarButtonsToRemove": [
                "zoom2d",
                "select2d",
                "lasso2d",
                "hoverCompareCartesian",
                "hoverClosestCartesian",
            ],
            "displayModeBar": True,
        }

        return fig.to_html(
            config=config, include_plotlyjs=True, full_html=False, div_id="radarChart"
        )

    def save_prediction(
        self, patient, risk_level, risk_score, probabilities, input_dict
    ):
        """
        Save the prediction and related details to the database.
        """
        # Calculate progress based on input_dict sum divided by 7925.57 and scaled to 100%
        input_sum = sum(input_dict.values())
        progress = min((input_sum / 7925.57) * 100, 100)

        # Create the QuestionnaireResponse instance
        response_instance = QuestionnaireResponse.objects.create(
            user=patient, progress=round(progress, 2), created_by=self.request.user
        )

        # Save the prediction result
        PredictionResult.objects.create(
            user=patient,
            questionnaire_response=response_instance,
            dob=patient.date_of_birth,
            risk_level=risk_level["level"],
            risk_score=risk_score,
            probability_benign=probabilities[0][0],
            probability_malignant=probabilities[0][1],
            chart_data=input_dict,
        )

        # Update the state of the response to completed
        response_instance.state = STATE.COMPLETED
        response_instance.save()

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        if data.get("is_save_prediction"):
            try:
                patient = data.get("user_id")
                input_dict = data.get("slider_data")

                patient = get_object_or_404(Account, pk=patient)

                # Generate predictions and related data
                context = self.populateData(input_dict)

                # Extract necessary data for saving the prediction
                probabilities = context["probabilities"]
                risk_level, risk_score = self.make_prediction(probabilities)

                # Save the prediction using the new save_prediction method
                self.save_prediction(
                    patient, risk_level, risk_score, probabilities, input_dict
                )
                logger.info(
                    f"Prediction saved successfully for user ID: {patient.id} by user: {request.user.username}"
                )
                log_user_activity(request, request.user, "Saved a prediction")
                return JsonResponse({"success": True})
            except Exception as e:
                logger.error(f"Error saving prediction: {e}", exc_info=True)
                return JsonResponse({"success": False, "error": str(e)})
        else:
            # Handle other POST logic here (e.g., previous logic that was already in post())
            input_dict = data.get("slider_data")
            context = self.populateData(input_dict)
            return JsonResponse(context)

    def get(self, request, *args, **kwargs):
        input_dict, sliders = self.add_sidebar()
        context = self.populateData(input_dict)
        context.update(
            {
                "sliders": sliders,
                "filter": AccountFilter(),
                "title_root": "Measurement",
            }
        )
        return render(request, self.template_name, context)

    def get_probability_summary(self, probability_malignant):
        """
        Get the appropriate summary based on the malignant probability.
        """
        for summary in PROBABILITY_SUMMARIES:
            range_match = re.search(r"(\d+)% - (\d+)% Malignancy", summary["range"])
            if range_match:
                lower_bound = float(range_match.group(1))
                upper_bound = float(range_match.group(2))
                if lower_bound <= probability_malignant * 100 <= upper_bound:
                    return summary
        return PROBABILITY_SUMMARIES[-1]

    def populateData(self, input_dict):
        """
        Populate data for rendering the view.
        """
        chart_data = self.get_radar_chart(input_dict)
        probabilities, prediction = self.add_predictions(input_dict)
        probability_benign = probabilities[0][0]
        probability_malignant = probabilities[0][1]

        summary = self.get_probability_summary(probability_malignant)
        prediction = int(prediction[0])

        context = {
            "benign": f"{probability_benign:.2f}",
            "malignant": f"{probability_malignant:.2f}",
            "radar_chart_data": chart_data,
            "prediction": prediction,
            "summary": summary["summary"],
            "recommendation": summary["recommendation"],
            "range": summary["range"],
            "probabilities": probabilities.tolist(),
        }

        return context


class AccountListAPIView(ActiveUserRequiredMixin, APIView):
    require_staff = True
    filter_backends = [DjangoFilterBackend]
    filterset_class = AccountFilter

    def get(self, request, *args, **kwargs):
        try:
            page_number = int(request.GET.get("page", 1))
            filterset = AccountFilter(
                request.GET, queryset=Account.objects.all().order_by("-id")
            )
            paginator = Paginator(filterset.qs, 5)

            page = paginator.get_page(page_number)
            users = page.object_list.values(
                "id", "username", "email", "first_name", "last_name"
            )
            log_user_activity(request, request.user, "Accessed account list")
            logger.info(f"User {request.user.username} accessed the account list.")

            return JsonResponse(
                {
                    "users": list(users),
                    "previous": (
                        page.previous_page_number() if page.has_previous() else None
                    ),
                    "next": page.next_page_number() if page.has_next() else None,
                    "total_pages": paginator.num_pages,
                }
            )
        except Exception as e:
            logger.error(f"Error in AccountListAPIView: {e}")
            return JsonResponse({"error": "Something went wrong."}, status=500)


class GenerateReportView(ActiveUserRequiredMixin, HelpResponse, View):
    require_staff = True
    chart_keys = {"mean": "mean", "worst": "worst", "standard_error": "se"}

    def get_data(self):
        """Retrieve prediction data based on the provided prediction ID."""
        prediction_id = self.kwargs.get("prediction_id")
        try:
            response_instance = get_object_or_404(
                PredictionResult.objects.select_related("questionnaire_response"),
                questionnaire_response__pk=prediction_id,
            )

            trained_model = self.request.trained_model
            score = response_instance.risk_score
            risk_level, risk_score = self.make_prediction(risk_score=score)
            probability_benign = response_instance.probability_benign
            probability_malignant = response_instance.probability_malignant
            progress = response_instance.questionnaire_response.progress
            created_by = response_instance.questionnaire_response.created_by
            chart_data = response_instance.chart_data
            log_user_activity(
                self.request,
                self.request.user,
                f"Generated report for Prediction ID {prediction_id}",
            )
            logger.info(
                f"User {self.request.user.username} generated a report for Prediction ID {prediction_id}."
            )

            features = []
            chart_keys = self.chart_keys
            for category in self.categories:

                features.append(
                    {
                        "Feature Name": category,
                        "Mean": chart_data.get(
                            self.generate_key(category, chart_keys["mean"]), "N/A"
                        ),
                        "Worst": chart_data.get(
                            self.generate_key(category, chart_keys["worst"]), "N/A"
                        ),
                        "Standard Error": chart_data.get(
                            self.generate_key(category, chart_keys["standard_error"]),
                            "N/A",
                        ),
                    }
                )

        except PredictionResult.DoesNotExist:
            logger.error("PredictionResult not found.")
            raise Http404("Prediction result not found.")

        return {
            "patient_id": f"BC{response_instance.user.usid}",
            "name": response_instance.user.full_name(),
            "age": calculate_age(response_instance.user.date_of_birth),
            "gender": response_instance.user.gender,
            "country": response_instance.user.country_name,
            "date_of_birth": response_instance.dob.strftime("%Y-%m-%d"),
            "date_of_prediction": response_instance.timestamp.strftime("%B %d, %Y"),
            "chart_data": chart_data,
            "risk_lvl": response_instance.risk_level,
            "risk_level": risk_level,
            "progress": progress,
            "risk_score": risk_score,
            "score": score,
            "created_by": created_by,
            "features": features,
            "probability_benign": probability_benign,
            "probability_malignant": probability_malignant,
            "model_type": trained_model.model_type,
            "model_version": trained_model.version,
            "training_dataset": "Wisconsin Breast Cancer Dataset",
            "accuracy": trained_model.accuracy,
            "precision": trained_model.precision,
            "recall": trained_model.recall,
            "f1_score": trained_model.f1_score,
        }

    def generate_chart(self, chart_data):
        chart_data = self.get_scaled_values(chart_data)
        categories = self.categories
        chart_keys = self.chart_keys
        chart_data = {
            "categories": categories,
            "mean": [
                chart_data.get(self.generate_key(category, chart_keys["mean"]), "N/A")
                for category in categories
            ],
            "worst": [
                chart_data.get(self.generate_key(category, chart_keys["worst"]), "N/A")
                for category in categories
            ],
            "standard": [
                chart_data.get(
                    self.generate_key(category, chart_keys["standard_error"]), "N/A"
                )
                for category in categories
            ],
        }

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
        try:

            data = self.get_data()
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()

            custom_styles = {
                "title": ParagraphStyle(
                    "Title", fontSize=24, spaceAfter=20, alignment=1
                ),
                "heading": ParagraphStyle(
                    "Heading", fontSize=16, spaceAfter=15, alignment=1
                ),
                "body": ParagraphStyle(
                    "Body",
                    fontSize=12,
                    spaceAfter=12,
                ),
                "footer": ParagraphStyle("Title", fontSize=18, spaceAfter=20),
            }

            elements.append(
                Paragraph("Breast Cancer Prediction Report", custom_styles["title"])
            )
            elements.append(
                Paragraph(
                    "Date: {}".format(data["date_of_prediction"]),
                    custom_styles["heading"],
                )
            )
            elements.append(Spacer(1, 30))

            # Patient Profile
            elements.append(Paragraph("Patient Profile", custom_styles["heading"]))
            patient_info = [
                ["Patient ID", data["patient_id"]],
                ["Name", data["name"]],
                ["Age", data["age"]],
                ["Gender", data["gender"]],
                ["Country", data["country"]],
                ["Date of Birth", data["date_of_birth"]],
                ["Date of Prediction", data["date_of_prediction"]],
            ]
            user_info_table = Table(patient_info, hAlign="CENTER")
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
            elements.append(Spacer(1, 50))

            # Risk Level
            risk_level = data["risk_level"]
            elements.append(Paragraph("Predicted Risk Level", custom_styles["heading"]))
            elements.append(Paragraph(f"Risk Level: {risk_level['info']}"))

            elements.append(Spacer(1, 50))
            elements.append(
                Paragraph("Probability Assessment", custom_styles["heading"])
            )
            risk_level_info = [
                [
                    "Probability of Being Benign",
                    "{:.2f}%".format(data["probability_benign"] * 100),
                ],
                [
                    "Probability of Being Malignant",
                    "{:.2f}%".format(data["probability_malignant"] * 100),
                ],
                ["Risk Category", data["risk_lvl"]],
                [
                    "Health History",
                    f"({data['progress']}%)",
                ],
            ]
            risk_level_table = Table(risk_level_info)
            risk_level_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ]
                )
            )
            elements.append(risk_level_table)

            # Clinical Features
            elements.append(Spacer(1, 30))
            # Convert the data to a format that can be used by the Table class
            table_data = [
                ["Feature Name", "Mean Value", "Worst Value", "Standard Error"]
            ]
            for feature in data["features"]:
                table_data.append(
                    [
                        feature["Feature Name"],
                        feature["Mean"],
                        feature["Worst"],
                        feature["Standard Error"],
                    ]
                )

            # Create and style the table
            features_table = Table(table_data, hAlign="CENTER")
            features_table.setStyle(
                TableStyle(
                    [
                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, 0),
                            colors.lightgrey,
                        ),  # Header background
                        (
                            "TEXTCOLOR",
                            (0, 0),
                            (-1, 0),
                            colors.black,
                        ),  # Header text color
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),  # Text alignment
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),  # Header font
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),  # Header padding
                        (
                            "BACKGROUND",
                            (0, 1),
                            (-1, -1),
                            colors.whitesmoke,
                        ),  # Row background color
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),  # Grid lines
                    ]
                )
            )

            # Build the document with the table
            elements.append(Spacer(1, 30))
            elements.append(Paragraph("Model Features", custom_styles["heading"]))
            elements.append(features_table)

            # Visual Analysis
            elements.append(Spacer(1, 30))
            elements.append(Paragraph("Visual Analysis", custom_styles["heading"]))
            chart_base64 = self.generate_chart(data["chart_data"])
            chart_img = Image(
                BytesIO(base64.b64decode(chart_base64)), width=500, height=300
            )
            elements.append(chart_img)
            elements.append(Spacer(1, 10))

            # # Predictive Model
            elements.append(Paragraph("Predictive Model", custom_styles["heading"]))
            model_info = [
                ["Model Type", data["model_type"]],
                ["Model Version", data["model_version"]],
                ["Training Dataset", data["training_dataset"]],
                ["Accuracy", f"{data['accuracy']}%"],
                ["Precision", f"{data['precision']}%"],
                ["Recall", f"{data['recall']}%"],
                ["F1-score", f"{data['f1_score']}%"],
            ]
            model_table = Table(model_info)
            model_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ]
                )
            )
            elements.append(model_table)

            # Recommendations
            elements.append(Spacer(1, 50))
            elements.append(Paragraph("Recommendations", custom_styles["heading"]))
            for rec in risk_level["recommendations"]:
                elements.append(Paragraph(rec["title"], custom_styles["heading"]))
                elements.append(Paragraph(rec["message"], custom_styles["body"]))
            elements.append(Spacer(1, 12))

            # Next Steps
            elements.append(Paragraph("Next Steps", custom_styles["heading"]))
            elements.append(Paragraph(risk_level["next"], custom_styles["body"]))
            for ns in risk_level["next_steps"]:
                elements.append(Paragraph(ns["subtitle"], custom_styles["heading"]))
                for msg in ns["messages"]:
                    elements.append(Paragraph(msg, custom_styles["body"]))
            elements.append(Spacer(1, 12))

            # Limitations
            elements.append(Paragraph("Limitations", custom_styles["heading"]))
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
                    "This report is generated based on the input data provided. For a more detailed analysis, consult a healthcare professional."
                )
            )
            elements.append(
                Paragraph(
                    "Confidentiality Notice: This report contains sensitive information. Handle with care."
                )
            )
            elements.append(Spacer(1, 30))
            elements.append(
                Paragraph(f"Created By {data['created_by']}", custom_styles["footer"])
            )

            doc.build(elements)
            pdf = buffer.getvalue()
            buffer.close()
            return pdf
        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            return HttpResponse("Failed to generate PDF.", status=500)

    def get(self, request, *args, **kwargs):
        pdf = self.generate_pdf()
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = 'inline; filename="patient_report.pdf"'
        response.write(pdf)
        return response


class FeatureExplanationView(ActiveUserRequiredMixin, TemplateView):
    require_staff = True
    template_name = "ml/feature_explanations.html"
    extra_context = {
        "title_root": "Feature Explanation",
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["feature_explanations"] = FEATURE_EXPLANATIONS
        context["feature_abbreviations"] = FEATURE_ABBRI
        log_user_activity(
            self.request, self.request.user, "Accessed feature explanations"
        )
        logger.info(f"User {self.request.user.username} accessed feature explanations.")

        return context


class TrainedModelListView(ActiveUserRequiredMixin, FilterView):
    require_staff = True
    model = TrainedModel
    context_object_name = "models"
    template_name = "ml/models.html"
    filterset_class = TrainedModelFilterFilter
    paginate_by = 5
    extra_context = {
        "title_root": "Model List",
    }

    def get(self, request, *args, **kwargs):
        log_user_activity(request, request.user, "Accessed trained models list")
        logger.info(f"User {request.user.username} accessed the trained models list.")

        return super().get(request, *args, **kwargs)


class TrainedModelDetailView(ActiveUserRequiredMixin, View):
    require_staff = True

    def get(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        try:
            model = TrainedModel.objects.get(pk=pk)

            # Log user activity
            log_user_activity(
                request, request.user, f"Viewed details of TrainedModel ID {pk}"
            )
            logger.info(
                f"User {request.user.username} viewed details of TrainedModel ID {pk}."
            )

            data = {
                "name": model.name.upper(),
                "version": model.version,
                "model_type": model.model_type,
                "accuracy": model.accuracy,
                "precision": model.precision,
                "recall": model.recall,
                "f1_score": model.f1_score,
                "date_trained": model.date_trained,
                "is_default": "Yes" if model.is_default else "No",
            }
            return JsonResponse(data)
        except TrainedModel.DoesNotExist:
            logger.error(f"TrainedModel ID {pk} not found.")
            return JsonResponse({"error": "Model not found."}, status=404)


class TestimonialListView(ActiveUserRequiredMixin, FilterView):
    require_staff = True
    model = Feedback
    context_object_name = "items"
    template_name = "ml/testimonials.html"
    filterset_class = FeedbackFilterFilter
    paginate_by = 10
    ordering = ["-submitted_at"]
    extra_context = {
        "title_root": "Testimonials",
    }

    def get(self, request, *args, **kwargs):
        log_user_activity(request, request.user, "Accessed testimonial list")
        logger.info(f"User {request.user.username} accessed the testimonial list.")
        return super().get(request, *args, **kwargs)


class TestimonialDeleteView(ActiveUserRequiredMixin, View):
    require_staff = True

    def post(self, request, *args, **kwargs):
        selected_ids = request.POST.getlist("selected_items")
        try:
            if selected_ids:
                contacts = Feedback.objects.filter(id__in=selected_ids)
                count = contacts.count()
                contacts.delete()
                messages.success(request, f"{count} feedback(s) deleted successfully.")
                log_user_activity(request, request.user, "DELETE TESTIMONIAL(s)")
                return JsonResponse({"success": True}, status=200)
            else:
                logger.warning(request, "DELETE_TESTIMONIALS: No Testimonial selected.")
                return JsonResponse(
                    {"success": False, "error": "No Testimonial selected."}, status=400
                )
        except Exception as e:
            logger.error(
                request,
                "DELETE_TESTIMONIALS",
                f"Error deleting Testimonials: {e}",
                level="ERROR",
            )
            return JsonResponse({"success": False, "error": str(e)}, status=400)


class TestimonialDetailView(ActiveUserRequiredMixin, View):
    require_staff = True

    def get(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        try:
            item = get_object_or_404(Feedback, pk=pk)
            rating_text = dict(RATE_CHOICES).get(item.rating, "Unknown Rating")
            data = {
                "user": (
                    item.result.user.full_name().title() if item.result.user else "Anonymous"
                ),
                "email": item.result.user.email if item.result.user else "N/A",
                "subject": rating_text,
                "message": item.message,
                "submitted_at": item.submitted_at.strftime("%Y-%m-%d %H:%M:%S"),
            }

            logger.info(f"VIEW_CONTACT_DETAIL: Contact details retrieved for ID {pk}.")
            log_user_activity(request, request.user, "VIEW CONTACT DETAIL")
            return JsonResponse(data)
        except Feedback.DoesNotExist:
            logger.warning(f"Feedback not found for ID {pk}.")
            return JsonResponse({"error": "Feedback not found."}, status=404)
        except Exception as e:
            logger.error(
                f"An error occurred while retrieving contact details for ID {pk}: {e}"
            )
            return JsonResponse({"error": "An unexpected error occurred."}, status=500)


class ToggleFeedbackShowView(ActiveUserRequiredMixin, View):
    require_staff = True

    def post(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        feedback = get_object_or_404(Feedback, pk=pk)

        try:
            if feedback.show:
                feedback.show = False
                message = "Feedback is now private."
            else:
                # Check if there are already 3 feedbacks marked as `show=True`
                shown_feedbacks = Feedback.objects.filter(show=True)
                if shown_feedbacks.count() >= 3:
                    oldest_feedback = shown_feedbacks.order_by("submitted_at").first()
                    oldest_feedback.show = False
                    oldest_feedback.save()
                    logger.info(
                        f"TOGGLE_FEEDBACK_SHOW: Feedback ID {oldest_feedback.pk} has been put to private to allow new feedback to be shown."
                    )
                feedback.show = True
                message = "Feedback is now public."

            feedback.save()
            logger.info(
                f"TOGGLE_FEEDBACK_SHOW: Show status toggled for Feedback ID {pk}."
            )
            log_user_activity(request, request.user, "TOGGLE FEEDBACK SHOW")
            return JsonResponse(
                {"success": True, "message": message, "new_status": feedback.show}
            )

        except Exception as e:
            logger.error(
                f"An unexpected error occurred while toggling show status for Feedback ID {pk}: {e}"
            )
            return JsonResponse({"error": "An unexpected error occurred."}, status=500)
