# Canvas-Api
Dap client documentation [here](https://data-access-platform-api.s3.amazonaws.com/client/index.html)

### DONE
Function for loading client id and secret from keyvault

```python
def getAzureKey(vault, key):
    '''Retrieve keys from the Azure keyvault with the vault name and key name'''
    from azure.keyvault.secrets import SecretClient
    from azure.identity import AzurePowerShellCredential
    
    #get credentials
    credential = AzurePowerShellCredential() 
    client = SecretClient(vault_url=f'https://{vault}.vault.azure.net', credential=credential)
    retrieved_secret = client.get_secret(name=key)
    
    return retrieved_secret.value
```

### Script for loading acces token
```python
def getCanvasAccessToken(client_id, clien_secret):
    import requests
    # Replace these with your actual values

    # Get Access Token
    token_url = 'https://api-gateway.instructure.com/ids/auth/login'
    token_data = {
        'grant_type': 'client_credentials'
    }

    response = requests.post(
        token_url,
        auth=(client_id, clien_secret),
        data=token_data
    )

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        access_token = response.json().get('access_token')
        from datetime import datetime, timedelta
        expdat = (datetime.now() + timedelta(hours=1)).strftime("%d/%m/%Y at %H:%M:%S")
        print(f'Retrieved access token succesfully: expires on {expdat}', )
        return access_token
    else:
        print('Failed to obtain Access Token. Status code:', response.status_code)
        print('Response:', response.text)
        exit()
```


### Script for loading all table info
```python

def getTableOverview(access_token):
    '''
    This fucntion gives an overview of all available tables in the data acces platfrom canavas API.
    It returns a list with all tables
    '''
    import requests
    uri = 'https://api-gateway.instructure.com/dap/query/canvas/table'
    headers = {
        'x-instauth': access_token
    }

    response = requests.get(uri, headers=headers)
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        table_names = response.json()
        print('Retrieved list of table names succesfully')
        return table_names['tables']
    else:
        print('Failed to make API call. Status code:', response.status_code)
        print('Response:', response.text)

```


### Script for loading table data job
```python

def getTableJobInfo(table, acces_token, df_format='csv'):
    '''
    THis function initiates a job request for a specific table. A job will be quued to download a dataframe in 
    the required format (defualt is csv). Ones the job is finnished the files can be downloaded. 
    '''

    import requests

    table_job_url = f'https://api-gateway.instructure.com/dap/query/canvas/table/{table}/data'
    headers = {
        'x-instauth': acces_token,
        'Content-type' : 'application/json'
    }
    data = {
        'format' : df_format,
        'mode' : 'expanded'
    }

    # initiate job
    request_table = requests.post(table_job_url, headers=headers, json=data)

    # check status code print message
    if request_table.status_code == 200:
        print('Job initiated succefully')
        return request_table
    else:
        print('Failed to make API call. Status code:', request_table.status_code)
        print('Response:', request_table.text)

```


### Script for checking job status
```python
def checkJobStatus(job_id,acces_token):
    '''
    A request is send to the server with the retreieved ID and checks if the job is ready.
    Once te job is ready the next script can be invoked
    '''

    import requests
    print('Running job status check this might take a while')
    status_url = f'https://api-gateway.instructure.com/dap/job/{job_id}'

    headers = {
        'x-instauth': acces_token,
    }

    # wait till job status is done
    import time
    request_status = requests.get(status_url ,headers=headers)
    if request_status.status_code == 200:
        status = request_status.json()['status']
        while status != 'complete':
            request_status = requests.get(status_url ,headers=headers)
            status = request_status.json()['status']
            time.sleep(5)
            print(status)
    else:
        print(f'Error with status code: {request_status.status_code}')

    print(request_status.json()['status'])

    # get object values of job
    return request_status.json()['objects']

```


### Script for downloading data to pandas dataframe

```python

def tableToPandasDataframe(acces_token, objects):
    import requests
        # now we can start downloading the different files
    headers = {
        'x-instauth': acces_token,
        'Content-type' : 'application/json'
    }
    # Make a POST request to the API
    request_urls = requests.post('https://api-gateway.instructure.com/dap/object/url', headers=headers, json=objects)
    if request_urls.status_code == 200:
        print('Urls loaded succefully')
    else:
        print('Failed to make API call. Status code:', request_table.status_code)
        print('Response:', request_urls.text)

    urls_json = request_urls.json()


    # get id's for loop
    ids = []
    for i in range(0,len(objects)):
        ids += [objects[i]['id']]

    file_urls = []

    # get urls from output
    for i in ids:     
        file_urls += [urls_json['urls'][i]['url']]

    import pandas as pd 
    from io import BytesIO 

    # set output df
    df = pd.DataFrame()

    for url in file_urls:
        request_file = requests.get(url, headers=headers)
        if request_file.status_code == 200:
                print('File downloaded succefully')
        else:
            print('Failed to make API call. Status code:', request_table.status_code)
            print('Response:', request_file.text)


        p = BytesIO(request_file.content)
        temp = pd.read_csv(p, compression='gzip',low_memory=False)
        df = pd.concat([temp,df], ignore_index=True)

    return df
```



### TO DO
Set filter in table select function
Error logging 
Extended documentation
Set timer for acces token and intitiate new call after 1 hour
