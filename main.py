
from Scripts.authentication import getAzureKey
client_id = getAzureKey('KV-DENA','KVK-API-CANVASDATA-2')
client_secret = getAzureKey('kV-DENA','KVS-API-CANVASDATA-2')

# retrieve accestoken
from Scripts.authentication import getCanvasAccessToken
access_token = getCanvasAccessToken(
    client_id=client_id,
    clien_secret=client_secret
    )

import requests


# Get Access Token
token_url = 'https://api-gateway.instructure.com/ids/auth/login'
token_data = {
    'grant_type': 'client_credentials'
}

response = requests.post(
    token_url,
    auth=(client_id, client_secret),
    data=token_data
)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    access_token = response.json().get('access_token')

    # add expiration time for token
    from datetime import datetime, timedelta
    expdat = (datetime.now() + timedelta(hours=1)).strftime("%d/%m/%Y at %H:%M:%S")
    print(f'Retrieved access token succesfully: expires on {expdat}', )


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


import base64
api_key = base64.b64encode(f"{client_secret}:{client_secret}".encode()).decode('utf-8')

# Setting up target API url
url = "https://api-gateway.instructure.com/ids/auth/login"  
payload = {'grant_type': 'client_credentials'}

headers = {
    'Authorization': f'Basic {api_key}',
    'Content-Type': 'application/x-www-form-urlencoded'
}

# POST request
response = requests.post(url, headers=headers, data=payload)

# Raise an exception if status code is not ok
response.raise_for_status()

try:
    # Converting the response into json for easy manipulation
    response_json = response.json()

    # Extracting token from the response
    access_token = response_json.get('access_token')

    # If access token is not found in the response, raise an exception
    if not access_token:
        raise ValueError("Access token not found in the response")
except ValueError:
    raise ValueError("Invalid JSON in the response")