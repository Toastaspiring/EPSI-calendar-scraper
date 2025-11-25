"""
Script to generate Outlook O365 token for the first time.
This must be run locally or in an interactive environment.
"""

import os
from O365 import Account, FileSystemTokenBackend
import base64

def generate_token():
    print("Outlook O365 Token Generator")
    print("----------------------------")

    client_id = input("Enter Client ID: ").strip()
    client_secret = input("Enter Client Secret: ").strip()

    if not client_id or not client_secret:
        print("Client ID and Client Secret are required.")
        return

    credentials = (client_id, client_secret)
    token_backend = FileSystemTokenBackend(token_path='.', token_filename='o365_token.txt')

    account = Account(credentials, token_backend=token_backend)

    # Authenticate
    # This will print a URL to visit
    scopes = ['basic', 'calendar_all']
    if account.authenticate(scopes=scopes):
        print("\nAuthentication successful!")
        print("Token saved to o365_token.txt")

        # Output base64 values for environment variables
        print("\n--- Environment Variable Values ---")

        # Credentials JSON Base64
        import json
        creds_json = json.dumps({
            'client_id': client_id,
            'client_secret': client_secret
        })
        creds_b64 = base64.b64encode(creds_json.encode('utf-8')).decode('utf-8')
        print(f"OUTLOOK_CREDENTIALS_JSON_BASE64={creds_b64}")

        # Token File Base64
        try:
            with open('o365_token.txt', 'rb') as f:
                token_data = f.read()
                token_b64 = base64.b64encode(token_data).decode('utf-8')
                print(f"OUTLOOK_TOKEN_TXT_BASE64={token_b64}")
        except Exception as e:
            print(f"Error reading token file: {e}")

    else:
        print("Authentication failed.")

if __name__ == '__main__':
    generate_token()
