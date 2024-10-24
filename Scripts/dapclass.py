import requests
import time
import pandas as pd
from io import BytesIO

class CanvasDataAPI:
    """
    A class to interact with the Canvas Data Access Platform (DAP) API, including
    retrieving tables, initiating table jobs, checking job statuses, and downloading data.
    """

    def __init__(self, access_token):
        """
        Initializes the CanvasDataAPI class with the provided access token.

        Args:
            access_token (str): Access token for authenticating API requests.
        """
        self.access_token = access_token
        self.base_url = 'https://api-gateway.instructure.com/dap'

    def get_table_overview(self):
        """
        Retrieves an overview of all available tables in the DAP Canvas API.

        Returns:
            list: A list of available table names if successful, None otherwise.
        """
        api_url = f'{self.base_url}/query/canvas/table'
        headers = {
            'x-instauth': self.access_token
        }

        response = requests.get(api_url, headers=headers)

        if response.status_code == 200:
            table_data = response.json()
            print('Successfully retrieved list of table names.')
            return table_data.get('tables', [])
        else:
            print(f'Failed to retrieve tables. Status code: {response.status_code}')
            print(f'Response: {response.text}')
            return None

    def initiate_table_job(self, table_name, data_format='csv'):
        """
        Initiates a job request for a specific table, allowing data download in the requested format.

        Args:
            table_name (str): The name of the table.
            data_format (str, optional): Desired file format for the downloaded data (default is 'csv').

        Returns:
            Response: The API response object if the job was initiated successfully, None otherwise.
        """
        job_url = f'{self.base_url}/query/canvas/table/{table_name}/data'
        headers = {
            'x-instauth': self.access_token,
            'Content-Type': 'application/json'
        }
        payload = {
            'format': data_format,
            'mode': 'expanded'
        }

        response = requests.post(job_url, headers=headers, json=payload)

        if response.status_code == 200:
            print('Job successfully initiated.')
            return response
        else:
            print(f'Failed to initiate job. Status code: {response.status_code}')
            print(f'Response: {response.text}')
            return None

    def check_job_status(self, job_id):
        """
        Checks the status of a job by its job ID and waits until the job is completed.

        Args:
            job_id (str): The job ID retrieved from the job initiation step.

        Returns:
            list: A list of job-related objects if the job is completed, None otherwise.
        """
        status_url = f'{self.base_url}/job/{job_id}'
        headers = {
            'x-instauth': self.access_token
        }

        print('Checking job status, this may take a while...')
        
        while True:
            response = requests.get(status_url, headers=headers)
            if response.status_code == 200:
                job_status = response.json().get('status', '')
                print(f'Job status: {job_status}')
                if job_status == 'complete':
                    return response.json().get('objects', [])
                time.sleep(5)
            else:
                print(f'Error checking job status. Status code: {response.status_code}')
                print(f'Response: {response.text}')
                return None

    def download_table_as_dataframe(self, job_objects):
        """
        Downloads the table data files and combines them into a Pandas DataFrame.

        Args:
            job_objects (list): A list of job objects with metadata for downloading files.

        Returns:
            DataFrame: A pandas DataFrame containing the combined data from the files.
        """
        headers = {
            'x-instauth': self.access_token,
            'Content-Type': 'application/json'
        }

        # Request download URLs
        url_request = requests.post(f'{self.base_url}/object/url', headers=headers, json=job_objects)
        
        if url_request.status_code == 200:
            print('Successfully retrieved URLs for file download.')
            download_urls = url_request.json().get('urls', {})
        else:
            print(f'Failed to retrieve download URLs. Status code: {url_request.status_code}')
            print(f'Response: {url_request.text}')
            return None

        # Download and concatenate the data files into a single DataFrame
        combined_df = pd.DataFrame()
        
        for obj in job_objects:
            file_id = obj.get('id')
            file_url = download_urls.get(file_id, {}).get('url', '')

            if not file_url:
                print(f'Failed to find URL for file ID: {file_id}')
                continue

            file_response = requests.get(file_url, headers=headers)

            if file_response.status_code == 200:
                print(f'Successfully downloaded file for ID: {file_id}')
                file_data = BytesIO(file_response.content)
                temp_df = pd.read_csv(file_data, compression='gzip', low_memory=False)
                combined_df = pd.concat([combined_df, temp_df], ignore_index=True)
            else:
                print(f'Failed to download file. Status code: {file_response.status_code}')
                print(f'Response: {file_response.text}')

        return combined_df
