from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header  = "PRLSS Admin"
admin.site.site_title   = "PRLSS"
admin.site.index_title  = "Dashboard"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("recommender.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler400 = "recommender.views.error_400"
handler404 = "recommender.views.error_404"
handler500 = "recommender.views.error_500"
