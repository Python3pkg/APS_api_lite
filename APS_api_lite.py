import pymssql
import os.path
import datetime

module_dir = os.path.dirname(__file__)  # Stored value for module directory, used for calling saved queries


def txt_to_str(file):
    """Simple function takes txt and converts it to str"""
    with open(file, 'r') as open_file:
        return open_file.read()


def edit_txt_query_with_start_and_end_date(query_string, start=None, end=None):
    """edits saved queries with start and end dates if they're supplied in the function,
    otherwise pass"""
    if start and end:
        start_str = start.strftime('%b %d %Y %I:%M%p')
        end_str = end.strftime('%b %d %Y %I:%M%p')
        trans_str = query_string.replace('--REPLACE--', '').\
            replace('%START_STR%', start_str).\
            replace('%END_STR%', end_str)
        return trans_str
    else:
        return query_string


def filter_query_results_according_to_filters_argument(query_results, filters=None):
    """Takes a nested list and searches for any list that contains an element in the 'filters' list
    If the 'filters' list is empty, return 'query_results'"""
    if filters:  # If filters is not empty, search the query for matches to the filter
        filtered_query = []
        for i in query_results:
            if any(j in i for j in filters):
                filtered_query.append(i)
        return filtered_query
    else:
        return query_results


class QueryResult(object):
    """Class for storing outputs of SQL queries

    Keyword Arguments:
        results -- output in form of nested lists of sql server query
        column_names -- column names according to query_results, derived from python dp_api

    """
    def __init__(self, results=None, column_names=None):
        self.results = results
        self.column_names = column_names



class APSConnection(object):
    """The primary class for conecting to the APS database

    Keyword Arguments:
        server -- server IP or host
        instance -- instance name
        user -- user id login to MSSQL
        password -- self-explanatory
        database -- database id at server/instance
    """
    def __init__(self, server=None, instance=None, user=None, password=None, database=None, desc=None):
        self.server = server
        self.instance = instance
        self.user = user
        self.password = password
        self.database = database
        self.desc = desc

    def connect(self):
        """Attempts to establish connection to SQL Server database."""
        conn = pymssql.connect(host=self.server+'\\'+self.instance,
                               user=self.user,
                               password=self.password,
                               database=self.database)
        return conn

    def general_query(self, query):
        """Directly queries database with given string; used in conjucton with specific methods."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(query)
        self.desc = cursor.description
        query_results = cursor.fetchall()
        return QueryResult(results=query_results, column_names=[i[0] for i in self.desc])

    def txt_query(self, file):
        """Runs query read from txt file at 'file' location."""
        return self.general_query(txt_to_str(file))

    def crane_transactions(self, start_date=None, end_date=None, filters=None):
        """Returns list of crane transactions between given times using premade query file."""
        trans_file = txt_to_str(module_dir + '\\' + 'queries\\crane_transactions')

        # First, edit the query with the start and end date- if it exists
        trans_query = edit_txt_query_with_start_and_end_date(trans_file, start=start_date, end=end_date)

         # Next, filter by the 'filters kwarg'- if it exists. Return the filtered query
        query_results = filter_query_results_according_to_filters_argument(self.general_query(trans_query).results,
                                                                           filters=filters)
        return QueryResult(results=query_results,
                           column_names=self.general_query(trans_query).column_names)  # Returns object type QueryResult

    def ocr_read_rates(self, start_date=None, end_date=None, filters=None):
        """Provides successful percentage of OCR read rates by crane between 2 given dates."""
        trans_file = txt_to_str(module_dir + '\\' + 'queries\\ocr_read_rate')

        # First, edit the query with the start and end date- if it exists
        trans_query = edit_txt_query_with_start_and_end_date(trans_file, start=start_date, end=end_date)

        # Next, filter by the 'filters kwarg'- if it exists. Return the filtered query
        query_results = filter_query_results_according_to_filters_argument(self.general_query(trans_query).results,
                                                                           filters=filters)
        return QueryResult(results=query_results,
                           column_names=self.general_query(trans_query).column_names)  # Returns object type QueryResult

