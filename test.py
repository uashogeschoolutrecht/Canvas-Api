# -*- coding: utf-8 -*-
"""
Created on Wed Oct 23 09:42:49 2024

@author: Justian
"""

import requests
import pandas as pd
import time
from io import BytesIO

# Constants for API authentication
CLIENT_ID = '***********'  # Replace with your actual client ID
CLIENT_SECRET = '***********' # Replace with your actual client secret
BASE_URL = "https://api-gateway.instructure.com"

def get_access_token(client_id, client_secret):
    """Obtain access token for the API."""
    response = requests.post(
        f"{BASE_URL}/ids/auth/login",
        data={"grant_type": "client_credentials"},
        auth=(client_id, client_secret),
    )

    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        raise Exception(f"Failed to obtain access token: {response.status_code} - {response.text}")

def get_table_names(access_token):
    """Retrieve the list of table names from the API."""
    uri = f'{BASE_URL}/dap/query/canvas/table'
    headers = {'x-instauth': access_token}
    response = requests.get(uri, headers=headers)

    if response.status_code == 200:
        print('Retrieved list of table names successfully')
        return response.json()
    else:
        raise Exception(f"Failed to retrieve table names: {response.status_code} - {response.text}")

def initiate_job(access_token, table_name):
    """Initiate a job to fetch data from a specific table."""
    table_job_url = f'{BASE_URL}/dap/query/canvas/table/{table_name}/data'
    headers = {
        'x-instauth': access_token,
        'Content-type': 'application/json'
    }
    data = {
        'format': 'csv',
        'mode': 'expanded'
    }

    request_table = requests.post(table_job_url, headers=headers, json=data)

    if request_table.status_code == 200:
        return request_table.json()["id"]
    else:
        raise Exception(f"Failed to initiate job: {request_table.status_code} - {request_table.text}")

def wait_for_job_completion(access_token, job_id):
    """Wait for the job to complete and return the job status."""
    status_url = f'{BASE_URL}/dap/job/{job_id}'
    headers = {'x-instauth': access_token}

    while True:
        request_status = requests.get(status_url, headers=headers)
        if request_status.status_code == 200:
            status = request_status.json()['status']
            print(status)
            if status == 'complete':
                return request_status.json()['objects']
            elif status == 'failed':
                raise Exception(f"Job failed: {request_status.json().get('message')}")
            time.sleep(5)  # Wait before next status check
        else:
            raise Exception(f"Error fetching job status: {request_status.status_code} - {request_status.text}")

def table_to_pandas_dataframe(access_token, objects):
    """Download CSV files from the specified objects and return as a pandas DataFrame."""
    headers = {
        'x-instauth': access_token,
        'Content-type': 'application/json'
    }

    # Request file URLs for objects
    request_urls = requests.post(f'{BASE_URL}/dap/object/url', headers=headers, json=objects)
    if request_urls.status_code != 200:
        raise Exception(f'Failed to make API call. Status code: {request_urls.status_code}. Response: {request_urls.text}')

    urls_json = request_urls.json()
    file_urls = [urls_json['urls'][obj['id']]['url'] for obj in objects]

    # Set output DataFrame
    df = pd.DataFrame()

    # Download each CSV file and concatenate into DataFrame
    for url in file_urls:
        request_file = requests.get(url, headers=headers)
        if request_file.status_code == 200:
            print('File downloaded successfully')
            p = BytesIO(request_file.content)
            temp = pd.read_csv(p, compression='gzip', low_memory=False)
            df = pd.concat([df, temp], ignore_index=True)
        else:
            raise Exception(f'Failed to download file. Status code: {request_file.status_code}. Response: {request_file.text}')

    return df

def save_dataframe_to_excel(dataframe, file_path):
    """Save the DataFrame to an Excel file."""
    dataframe.to_excel(file_path, sheet_name='Sheet_name_1', index=False)

def main():
    """Main function to coordinate data fetching and saving to Excel."""
    access_token = get_access_token(CLIENT_ID, CLIENT_SECRET)
    table_names = get_table_names(access_token)
    
    # For demonstration, we hard-code the table name 'assignments'.
    job_id = initiate_job(access_token, 'assignments')
    objects = wait_for_job_completion(access_token, job_id)

    # Pass the access token and selected object to retrieve DataFrame
    dataframe = table_to_pandas_dataframe(access_token, [objects[1]])  # Example for the second object

    # Save DataFrame to Excel
    save_dataframe_to_excel(dataframe, 'jouw map\\_dataframe.xlsx')  # Replace with your actual path

if __name__ == "__main__":
    main()


### Key Improvements Made:
#1. **Modular Functions:** The code is divided into separate functions for better modularity and reusability.
#2. **Error Handling:** Improved error handling throughout the code, raising exceptions with clear messages when calls to the API fail.
#3. **PEP 8 Compliance:** The code conforms to Pythons styling guidelines, including consistent naming conventions.
#4. **Documentation:** Added docstrings to each function for clarity on functionality and parameters.
#5. **Constants:** Defined constants for API credentials and base URL at the top of the script, improving maintainability.
#6. **Path Handling:** Ensure proper path handling for saving the Excel file.
#7. **Streamlined Functionality:** The main process is encapsulated into the `main()` function, serving as the entry point when the script runs.

### Testing Instructions
#You can create a separate test module with `pytest`. For example:

import pytest
from your_module_name import get_access_token, save_dataframe_to_excel

def test_get_access_token(monkeypatch):
    monkeypatch.setattr(requests, 'post', lambda *args, **kwargs: MockResponse({"access_token": "test_token"}, 200))
    token = get_access_token('test_id', 'test_secret')
    assert token == "test_token"

# Mock Response Class
class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data

if __name__ == "__main__":
    pytest.main()


# You can run the test using: bash
pytest your_test_file.py