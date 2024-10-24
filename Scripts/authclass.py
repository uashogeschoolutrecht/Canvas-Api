from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
from datetime import datetime, timedelta
import requests

class APIAccessManager:
    """
    A class to manage API access, including retrieving secrets from Azure Key Vault and
    obtaining access tokens for the Canvas API.
    """

    def __init__(self, vault_name):
        """
        Initializes the APIAccessManager class with the provided Azure Key Vault name.

        Args:
            vault_name (str): The name of the Azure Key Vault.
        """
        self.vault_url = f'https://{vault_name}.vault.azure.net'
        self.credential = DefaultAzureCredential()
        self.client = SecretClient(vault_url=self.vault_url, credential=self.credential)

    def get_azure_key(self, key_name):
        """
        Retrieves a secret from the Azure Key Vault by key name.

        Args:
            key_name (str): The name of the key to retrieve from the Key Vault.

        Returns:
            str: The value of the retrieved secret.
        """
        retrieved_secret = self.client.get_secret(name=key_name)
        return retrieved_secret.value

    def get_canvas_access_token(self, client_id, client_secret):
        """
        Obtains an access token for the Canvas Data Access Platform (DAP) API using
        client credentials.

        Args:
            client_id (str): The client ID for Canvas API authentication.
            client_secret (str): The client secret for Canvas API authentication.

        Returns:
            str: The access token for Canvas API.
        """
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

            # Add expiration time for the token
            exp_time = (datetime.now() + timedelta(hours=1)).strftime("%d/%m/%Y at %H:%M:%S")
            print(f'Retrieved access token successfully: expires on {exp_time}')
            return access_token
        else:
            print('Failed to obtain Access Token. Status code:', response.status_code)
            print('Response:', response.text)
            exit()
