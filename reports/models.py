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

        # build up a where clause from passed filters
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
            closure to format results as a usable an ordered dict
            :return: order dictionary
            """
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

        return fetch_all_as_ordered_dict()
