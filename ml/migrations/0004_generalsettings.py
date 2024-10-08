# Generated by Django 5.0.6 on 2024-08-13 17:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ml', '0003_alter_emailsettings_email_subject_prefix'),
    ]

    operations = [
        migrations.CreateModel(
            name='GeneralSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('site_name', models.CharField(default='MyProject', max_length=255)),
                ('company', models.CharField(default='Zila Tech', max_length=255)),
                ('tagline', models.CharField(default='Zila Tech', max_length=255)),
                ('site_description', models.TextField(blank=True, null=True)),
                ('allow_registration', models.BooleanField(default=True)),
                ('maintenance_mode', models.BooleanField(default=False)),
            ],
        ),
    ]
