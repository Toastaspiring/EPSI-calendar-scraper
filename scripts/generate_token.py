import os
import pickle
import base64
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/calendar']

def main():
    print("--- Google Calendar Token Generator ---")

    if not os.path.exists('credentials.json'):
        print("Error: credentials.json not found in the current directory.")
        print("Please download your OAuth 2.0 Client ID credentials from Google Cloud Console")
        print("and save it as 'credentials.json' in this directory.")
        return

    print("Starting authentication flow...")
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)

    print("\nAuthentication successful!")

    # Save the credentials for the next run
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)
    print("Saved token.pickle")

    # Read and encode token.pickle
    with open('token.pickle', 'rb') as token_file:
        token_data = token_file.read()
        token_b64 = base64.b64encode(token_data).decode('utf-8')

    print("\n--- SETUP INSTRUCTIONS ---")
    print("1. Go to your GitHub Repository > Settings > Secrets and variables > Actions")
    print("2. Create a new Repository Secret named 'GOOGLE_TOKEN_PICKLE_BASE64'")
    print("3. Paste the following string as the value:")
    print("-" * 20)
    print(token_b64)
    print("-" * 20)

    # Also encode credentials.json just in case
    with open('credentials.json', 'rb') as creds_file:
        creds_data = creds_file.read()
        creds_b64 = base64.b64encode(creds_data).decode('utf-8')

    print("\n(Optional) If you want to support token refreshing even if the pickle invalidates widely (though refresh token is inside pickle):")
    print("Create a secret named 'GOOGLE_CREDENTIALS_JSON_BASE64' with this value:")
    print("-" * 20)
    print(creds_b64)
    print("-" * 20)

if __name__ == '__main__':
    main()
