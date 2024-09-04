from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import path, include
from django.conf.urls import handler500, handler403, handler404, handler400

handler500 = "patients.views.error500view"
handler403 = "patients.views.error403view"
handler404 = "patients.views.error404view"
handler400 = "patients.views.error400view"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("AdminHub/", include("ml.urls")),
    path("", include("patients.urls")),
    path("auth/", include("accounts.urls")),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
