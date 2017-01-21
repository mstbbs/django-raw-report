from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from reports.helpers import get_report_type


@login_required(login_url='/admin/login/')
def report_menu(request):
    return render(request, 'admin/reports/report_menu.html')


@login_required(login_url='/admin/login/')
def show_report(request, report_type):
    # you could create a new form, in forms.py and import it here
    # then you could check if the request is GET or POST and either
    # return the form or clean and parse the form and pass to your
    # chosen report. Here we will just hard-code a filter
    filters = {
        "email": "michael@whetten.com"
    }
    report = get_report_type(report_type)(filters=filters)
    data = report.run_report()
    # in this example we are looking to render html
    context = report.tabulate_data(data)
    return render(request, 'admin/reports/html_results.html', context)
