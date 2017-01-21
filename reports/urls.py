from django.conf.urls import url

from reports.views import show_report

urlpatterns = [
    url(r'^(?P<report_type>[\w-]+)/$', show_report, name="show_report"),
]
