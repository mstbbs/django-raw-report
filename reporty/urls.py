from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^admin/reports/', include("reports.urls", namespace="reports")),
    url(r'^admin/', admin.site.urls),
]
