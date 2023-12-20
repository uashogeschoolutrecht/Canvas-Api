def getAzureKey(vault, key):
    '''Retrieve keys from the Azure keyvault with the vault name and key name'''
    from azure.keyvault.secrets import SecretClient
    from azure.identity import AzurePowerShellCredential
    
    #get credentials
    credential = AzurePowerShellCredential() 
    client = SecretClient(vault_url=f'https://{vault}.vault.azure.net', credential=credential)
    retrieved_secret = client.get_secret(name=key)
    
    return retrieved_secret.value


def getCanvasAccessToken(client_id, clien_secret):
    '''
    Loads an overview of all available tables from the data acces platform.
   	'''
    import requests
    

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

        # add expiration time for token
        from datetime import datetime, timedelta
        expdat = (datetime.now() + timedelta(hours=1)).strftime("%d/%m/%Y at %H:%M:%S")
        print(f'Retrieved access token succesfully: expires on {expdat}', )
        return access_token
    else:
        print('Failed to obtain Access Token. Status code:', response.status_code)
        print('Response:', response.text)
        exit()
