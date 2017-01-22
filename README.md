## Step 1: Confirm your settings 

### 1a. Make sure you have APP_DIRS set to True

```
TEMPLATES = [
   {
       'BACKEND': 'django.template.backends.django.DjangoTemplates',
       'DIRS': [],
       'APP_DIRS': True,
       'OPTIONS': {
           'context_processors': [
               'django.template.context_processors.debug',
               'django.template.context_processors.request'
           ],
       },
   },
]
```

### 1b. Make sure you have included your app (reports) in the INSTALLED_APPS section:

```
INSTALLED_APPS = (
   'django.contrib.admin',
   'django.contrib.auth',
   'django.contrib.contenttypes',
   'django.contrib.sessions',
   'django.contrib.messages',
   'django.contrib.staticfiles',
   'django.contrib.gis',
   'reports'   
)
```

## Step 2: Map your URLs

It will make your life hella easier to design django apps along this workflow: define url → update view → update model. The majority of the out-of-the-box admin is model driven with just two views available to override: list records, edit record. As your report is neither of these you will need a custom url, view, and template. If you want to create adhoc reports you may also want to create a custom form for each report. 

Anyways, urls. This first file is the _project's_ main urls.py file. Here we create our custom admin url for our app. We will route all urls starting with `/admin/reports/` (notice there is no closing `$`) to our report app's urls.py file:

```
# reporty.urls.py

from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
   url(r'^admin/reports/', include("reports.urls", namespace="reports")),
   url(r'^admin/', admin.site.urls),
]
```

Ok, now we are in our report app's urls.py file. I tossed two url examples in here. The first one sets a `report_name` variable to the url path and passes it to a `show_report` function. The second url would be used for a general report's menu screen (not part of this example):

```
# reports.urls.py:
from django.conf.urls import url

from reports.views import show_report

urlpatterns = [
   url(r'^(?P<report_type>[\w-]+)/$', show_report, name="show_report"),
   url(r'^$', report_menu, name="report_menu"),
]
```

In the examples that follow I have a single report named `users`. Navigating to `/admin/reports/email/` will pass `report_type="email"` to `reports.views.show_report()`.


## Step 3: Write your custom view

Views should be light-weight. That means using models to get/format data and then whipping it together with simple, context specific functions in the view. We decorate the functions with `@login_required` so that they use admin auth. You would most likely be passing filters through a form - but for now we will:
  - instantiate the correct subclass from the `report_type`
  - run the report
  - format the report
  - return the view

```
# reports.views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from reports.helpers import get_report_type


@login_required(login_url='/admin/login/')
def report_menu(request):
   """
   view used to list all reports available.
   """
   return render(request, 'admin/reports/report_menu.html')


@login_required(login_url='/admin/login/')
def show_report(request, report_type):
   """
   a single report. 
   TODO: try/except for reports that don't exist.
   """
   context = {}
   # you could create a new form, in forms.py and import it here
   # then you could check if the request is GET or POST and either
   # return the form or clean and parse the form and pass to your
   # chosen report. Here we will just hard-code a filter
   filters = {
       "email": "michael@whetten.com"
   }
   # in this example we are looking to render as html
   # so format the data towards that end
   report = get_report_type(report_type)(filters=filters)
   data = report.run_report()
   context = report.tabulate_data(data)
   return render(request, 'admin/reports/html_results.html', context)

```
 

# Step 4: Ok, now you’re cooking. Models Time!

You could keep references to your available reports in the database but I just threw together a quick helpers.py to map the url to the correct class:

```
# reports.helpers.py
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
```

Now for the meat.

```
# reports.models.py
from django.db.models.query import connections
from django.contrib.auth.models import User


class Report(object):
   def __init__(self, filters=None):
       self.filters = filters or {}

   @staticmethod
   def tabulate_data(results):
       """
       All result rows have the same keys, push them all into a header
       :param results: ordered dict
       :return: dict
       """
       headers = []
       if results:
           headers = results[0].keys()
       records = []
       for record in results:
           records.append(record.values())
       context = {'headers': headers,
                  'records': records}
       return context

   def run_report(self):
       return []


class EmailReport(Report):
   def run_report(self):
       # init your connection
       cursor = connections["default"].cursor()

       # build up a where clause from passed/cleaned filters
       where_clause = """
                     AND au.email = "{0}"
                     ORDER BY au.date_joined
                   """.format(self.filters.get('email'))

       # build up the sql as a multi-line string
       sql = """
           SELECT
               au.first_name,
               au.last_name,
               au.email as username
           FROM auth_user au
           LEFT OUTER JOIN auth_user_groups aug on au.id = aug.user_id
           WHERE 1=1"""

       sql += " {0}".format(where_clause)

       # run the sql
       cursor.execute(sql)

       def fetch_all_as_ordered_dict():
           """
           closure to format results as an ordered dict
           :return: order dictionary
           """
           columns = [col[0] for col in cursor.description]
           return [dict(zip(columns, row)) for row in cursor.fetchall()]

       return fetch_all_as_ordered_dict()

```

## Step 5: Make your template

In your reports app create a folder called `/templates/admin/reports`

This is your override folder for the app. If you create a file with the same name as a base-admin template file it will override that template. But you can also create your own custom templates that map to your views.

Within your custom templates you should extend the `admin/base_site.html` so that your new page looks like all the other pages in the admin. You can override blocks like a boss. Just inspect the default `base_site.html` to see what blocks are available for override.

Default admin templates are located in the django package at: `...path_to_your_virtual_env.../site-packages/django/contrib/admin/templates/admin/`


```
{# reports/tempates/admin/html_results.html #}

{% extends "admin/base_site.html" %}

{% block content %}
 {% if records %}
   <table class="table">
     <thead>
     <tr>
       {% for header in headers %}
         <th>{{ header }}</th>
       {% endfor %}
     </tr>
     </thead>
     <tbody>
     {% for record in records %}
       <tr>
         {% for value in record %}
           <td>{{ value }}</td>
         {% endfor %}
       </tr>
     {% endfor %}
     </tbody>
   </table>
 {% else %}
   <p>No records match your search criteria.</p>
 {% endif %}
{% endblock %}

```

That’s it. 

Add some forms and conditions for get and post and you have a pretty solid adhoc reporting app. 
