# Generated by Django 5.0.6 on 2024-08-13 22:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ml', '0006_alter_generalsettings_allow_registration_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='EmailSettings',
        ),
        migrations.DeleteModel(
            name='GeneralSettings',
        ),
    ]
