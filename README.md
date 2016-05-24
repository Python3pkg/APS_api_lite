## Synopsis

This library is meant to provide a basic mini-API for accessing APS Technologies crane OCR database via python by acting as 
a wrapper for the pymssql library that makes use of the Python database API Specifications

***

This library revolves around the APS_api_lite.QueryResult and APS_api_lite.APSConnection class. These two classes are 
shown below

```
class QueryResult(object):
    """Class for storing outputs of SQL queries

    Keyword Arguments:
        results -- output in form of nested lists of sql server query
        column_names -- column names according to query_results, derived from python dp_api

    """
    def __init__(self, results=None, column_names=None):
        self.results = results
        self.column_names = column_names
```

```
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
```
***
***
## Example

Create an APSConnection class with the SQL Server credentials to connect to the database

```python
import APS_api_lite as aps

database = aps.APSConnection(server='127.0.0.1',instance='sqlexpress', user='user',password='hunter2',
                             database='OCS')
```
***

There are three methods used to extract relevant crane transactions data: crane_transactions, mm_read_rate, and 
ocr_read_rate. These respectively measure the individual crane transactions, the matchmaker success rate, and the ocr
module's success rate at identifying the container numbers.

```python
import APS_api_lite as aps
import datetime

database = aps.APSConnection(server='127.0.0.1',instance='sqlexpress_2008', user='user',password='hunter2',
                             database='OCS')

end = datetime.datetime.now()  # Choose 'now' as end date
start = end + datetime.timedelta(hours=-24)  # Choose 24 hours ago as start date
filters = ['CR07', 'CR06']

mm_read_rates = database.mm_read_rates(start_date=start, end_date=end, filters=filters)
crane_transactions = database.crane_transactions(start_date=start, end_date=end, filters=filters)
ocr_read_rates = database.ocr_read_rates(start_date=start, end_date=end, filters=filters)
```
The 'filters' keyword argument is a list of strings that is checked against each row for a match. It can be used to 
filter any column item in the database
***

Since these methods return are of the QueryResults class, the query results (in the form of a nested loop), and the
column names can be found by calling the attribute names.

```python
print(mm_read_rates.results, mm_read_rates.column_names)


>> [('CR07', 112, 112, Decimal('1.000000000000')), ('CR06', 136, 136, Decimal('1.000000000000'))] ,
>> ['crane', 'goodmm', 'totalcontainer', 'read_rate']
```
***
***

## Editing/Adding Queries
Queries are stored as .txt files in the /queries/ directory located in the installation directory of the library. The
The pymssql module executes these as strings crane_transactions query is shown below

```SQL
select z.TrxnStartTS, z.TrxnEndTS, a.TransactionID, z.OCRNodeName,a.OCRNumber as container_1, a.Position as position_1,

case
when a.ContainerType != 'TWIN_TWENTY'
then null
else
c.OCRNumber end as container_2,

case
when a.ContainerType != 'TWIN_TWENTY'
then null
else
c.position end as position_2,
b.OCRNumber as truck,a.ContainerType, z.MoveType

from
OCSTransaction as z
left join
OCSscan as a
on z.id = a.TransactionID
left join
ocsscan as c
on a.TransactionID = c.TransactionID
left join
OCSScan as b
on a.TransactionID = b.TransactionID

where a.OCRComponent = 'Container' and (b.OCRComponent = 'MatchMaker' or z.MoveType = 'SHP_TO_SHP' or z.MoveType ='HATCHLID_DISCHARGE') and c.OCRComponent = 'container' and a.Position!='RIGHT' and c.Position!='LEFT'
--REPLACE-- and z.TrxnStartTS between convert(datetime, '%START_STR%') and convert(datetime, '%END_STR%')
order by a.TransactionID desc
````

The line that reads 
```SQL
--REPLACE-- and z.TrxnStartTS between convert(datetime, '%START_STR%') and convert(datetime, '%END_STR%')
```
is uncommented and edited to adjust the date filters for a query
