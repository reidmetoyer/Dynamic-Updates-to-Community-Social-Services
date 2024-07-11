import os
from flask import Flask, request
import gspread
from google.oauth2 import service_account
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
from google.cloud import secretmanager
import json

load_dotenv()

app = Flask(__name__)

client = secretmanager.SecretManagerServiceClient()

secret_name = os.getenv("SECRET_NAME")
project_id = os.getenv("PROJECT_ID")
name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"

response = client.access_secret_version(name=name)
secret_data = response.payload.data.decode("UTF-8")

# Google Sheets setup
#creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "/app/credentials.json")
#print(creds_path)

with open("/app/credentials.json", "W") as f:
    f.write(secret_data)
    
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("/app/credentials.json", scope)
client = gspread.authorize(creds)


# Access the spreadsheet by key
spreadsheet_key = "1nc4ZbHfiJyCkXNuUe_WhsMVTNfrwoYaPcGLH5JE2Xiw"
sheet = client.open_by_key(spreadsheet_key).sheet1

@app.route('/response', methods=['GET'])
def response():
    answer = request.args.get('answer')
    sheet.append_row([answer])
    return "Thank you for your response!"

if __name__ == "__main__":
    print("creating port...")
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=8080)
