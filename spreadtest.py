import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

# Set the path to your service account credentials file
print("creds")
credentials_path = 'credentials.json'

# Verify the file path
if not os.path.exists(credentials_path):
    raise FileNotFoundError(f"Credentials file not found at {credentials_path}")

# Define the scope
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Authenticate using the service account
creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
client = gspread.authorize(creds)
print(creds)

# Define the Google Spreadsheet key
spreadsheet_key = "1nc4ZbHfiJyCkXNuUe_WhsMVTNfrwoYaPcGLH5JE2Xiw"

# Attempt to open the spreadsheet
try:
    sheet = client.open_by_key(spreadsheet_key).sheet1
    print("Successfully accessed the spreadsheet.")
    # Optionally, read some data to ensure read access
    print(sheet.get_all_records())
except gspread.exceptions.SpreadsheetNotFound:
    print("Spreadsheet not found or access denied.")
except Exception as e:
    print(f"An error occurred: {e}")
    import traceback
    traceback.print_exc()
