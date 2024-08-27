from .models import GeneralSettings  # Assuming you have a GeneralSettings model


def general_settings(request):
    data = {
        "site_name": "QuickDiag",
        "site_company": "Zila Tech",
        "site_telephone": "(123) 456-7890",
        "site_contact_email": "info.quickdiag@gmail.com",
        "site_address": " 123 Main Street, Paraku Estate, XEZ",
        "site_tagline": "Empowering Early Detection, Saving Lives",
        "site_description": "",
        "site_allow_registration": True,
        "site_maintenance_mode": False,
    }
    try:
        settings = GeneralSettings.objects.first()
        return {
            "site_name": settings.site_name or data["site_name"],
            "site_company": settings.company or data["site_company"],
            "site_tagline": settings.tagline or data["site_tagline"],
            "site_description": settings.site_description or data["site_description"],
            "site_allow_registration": settings.allow_registration
            or data["site_allow_registration"],
            "site_maintenance_mode": settings.maintenance_mode
            or data["site_maintenance_mode"],
            "site_telephone": settings.telephone,
            "site_contact_email": settings.contact_email,
            "site_address": settings.address,
        }
    except GeneralSettings.DoesNotExist:
        return data
