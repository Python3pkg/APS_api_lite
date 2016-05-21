import pymssql
import os.path
import datetime

module_dir = os.path.dirname(__file__)  # Stored value for module directory


def txt_to_str(file):
    """Simple function takes txt and converts it to str"""
    with open(file, 'r') as open_file:
        return open_file.read()


class QueryResult(object):
    """Class for storing outputs of SQL queries

    Keyword Arguments:
        results -- output in form of nested lists of sql server query
        column_names -- column names according to

    """
    def __init__(self, results=None, column_names=None, description=None):
        self.results = results
        self.column_names = column_names
        self.description = description


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
        return cursor.fetchall()

    def txt_query(self, file):
        """Runs query read from txt file at 'file' location."""
        return self.general_query(txt_to_str(file))

    def crane_transactions(self, start_date=None, end_date=None, filters=None):
        """Returns list of crane transactions between given times using premade query file."""
        trans_file = txt_to_str(module_dir + '\\' + 'queries\\crane_transactions')
        if start_date and end_date:  # If start and end time are specified, edit the query to include it
            start_str = start_date.strftime('%b %d %Y %I:%M%p')
            end_str = end_date.strftime('%b %d %Y %I:%M%p')
            trans_file = trans_file.replace('--REPLACE--', '').replace('%START_STR%', start_str).replace('%END_STR%', end_str)
        if filters:  # If filters is not empty, search the query for matches to the filter
            filtered_query = []
            for i in self.general_query(trans_file):
                if any(j in i for j in filters):
                    filtered_query.append(i)
            return QueryResult(results=filtered_query, description=self.desc)  # Returns object type QueryResult
        else:
            return QueryResult(results=self.general_query(trans_file), description=self.desc)

    def ocr_read_rates(self, start_date=None, end_date=None, filters=None):
        """Provides successful percentage of OCR read rates by crane between 2 given dates."""
        trans_file = txt_to_str(module_dir + '\\' + 'queries\\ocr_read_rate')
        if start_date and end_date:  # If start and end time are specified, edit the query to include it
            start_str = start_date.strftime('%b %d %Y %I:%M%p')
            end_str = end_date.strftime('%b %d %Y %I:%M%p')
            trans_file = trans_file.replace('--REPLACE--', '').replace('%START_STR%', start_str).replace('%END_STR%', end_str)
        if filters:  # If filters is not empty, search the query for matches to the filter
            filtered_query = []
            for i in self.general_query(trans_file):
                if any(j in i for j in filters):
                    filtered_query.append(i)
            return QueryResult(results=filtered_query, description=self.desc)  # Returns object type QueryResult
        else:
            return QueryResult(results=self.general_query(trans_file), description=self.desc)
