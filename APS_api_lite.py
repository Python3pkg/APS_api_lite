import pymssql
import re
from os import listdir
import os.path
import datetime


class APS_Connection(server='',instance='', user='', pw=''):

    def