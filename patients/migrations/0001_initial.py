# Generated by Django 5.0.6 on 2024-08-12 23:31

import django.db.models.deletion
import django.db.models.functions.datetime
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('subject', models.CharField(max_length=200, null=True)),
                ('email', models.EmailField(max_length=254)),
                ('message', models.TextField()),
                ('submitted_at', models.DateTimeField(db_default=django.db.models.functions.datetime.Now())),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(choices=[(1, 'Very Poor'), (2, 'Poor'), (3, 'Average'), (4, 'Good'), (5, 'Excellent')])),
                ('message', models.TextField()),
                ('submitted_at', models.DateTimeField(db_default=django.db.models.functions.datetime.Now())),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='QuestionnaireResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('progress', models.FloatField(db_default=0)),
                ('submission_date', models.DateTimeField(db_default=django.db.models.functions.datetime.Now())),
                ('updated_date', models.DateTimeField(auto_now=True, db_default=django.db.models.functions.datetime.Now())),
                ('state', models.CharField(choices=[('Pending', 'Pending'), ('In Progress', 'In Progress'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')], default='Pending', max_length=20)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='creator', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PredictionResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dob', models.DateField(null=True, verbose_name='Birthday')),
                ('risk_level', models.CharField(max_length=20)),
                ('risk_score', models.DecimalField(decimal_places=2, max_digits=5)),
                ('probability_benign', models.DecimalField(decimal_places=2, max_digits=5)),
                ('probability_malignant', models.DecimalField(decimal_places=2, max_digits=5)),
                ('chart_data', models.JSONField()),
                ('submission_date', models.DateTimeField(db_default=django.db.models.functions.datetime.Now())),
                ('timestamp', models.DateTimeField(auto_now=True, db_default=django.db.models.functions.datetime.Now())),
                ('deleted', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('questionnaire_response', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='patients.questionnaireresponse')),
            ],
        ),
        migrations.CreateModel(
            name='Response',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_key', models.CharField(max_length=50)),
                ('questionnaire_response', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='responses', to='patients.questionnaireresponse')),
            ],
        ),
    ]
