from reports.models import EmailReport

"""
This could all be abstracted out into a proper model to track reports to classes.
For simplicity I'm just doing it all in data structures
"""

EMAIL_REPORT = EmailReport

REPORTS_TYPES = {
    'email': EMAIL_REPORT
}


def get_report_type(report_type):
    return REPORTS_TYPES.get(report_type, None)
