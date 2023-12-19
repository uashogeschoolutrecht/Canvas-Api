
from Scripts.authentication import getAzureKey
client_id = getAzureKey('kV-DENA','KVK-CANVAS-API-DEV')
client_secret = getAzureKey('kV-DENA','KVS-CANVAS-API-DEV')

# retrieve accestoken
from Scripts.authentication import getCanvasAccessToken
access_token = getCanvasAccessToken(
    client_id=client_id,
    clien_secret=client_secret
    )

from Scripts.dapfuncs import getTableOverview
tabel_overview = getTableOverview(access_token=access_token)

# set table name
table = 'calendar_events'

# Initiate jobs
from Scripts.dapfuncs import getTableJobInfo
request_table = getTableJobInfo(table, access_token)

# get job Id's for download
from Scripts.dapfuncs import checkJobStatus
objects = checkJobStatus(request_table.json()['id'],access_token)

from Scripts.dapfuncs import tableToPandasDataframe
df = tableToPandasDataframe(access_token,objects)

