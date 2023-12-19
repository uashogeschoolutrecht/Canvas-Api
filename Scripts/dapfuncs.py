

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

def getTableJobInfo(table, access_token, df_format='csv'):
    '''
    THis function initiates a job request for a specific table. A job will be quued to download a dataframe in 
    the required format (defualt is csv). Ones the job is finnished the files can be downloaded. 
    '''

    import requests

    table_job_url = f'https://api-gateway.instructure.com/dap/query/canvas/table/{table}/data'
    headers = {
        'x-instauth': access_token,
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

# check job status
def checkJobStatus(job_id,access_token):
    '''
    A request is send to the server with the retreieved ID and checks if the job is ready.
    Once te job is ready the next script can be invoked
    '''

    import requests
    print('Running job status check this might take a while')
    status_url = f'https://api-gateway.instructure.com/dap/job/{job_id}'

    headers = {
        'x-instauth': access_token,
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


def tableToPandasDataframe(access_token, objects):
    import requests
        # now we can start downloading the different files
    headers = {
        'x-instauth': access_token,
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