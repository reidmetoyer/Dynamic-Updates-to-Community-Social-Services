import os
from flask import Flask, request, jsonify
import gspread
from google.oauth2 import service_account
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
from google.cloud import secretmanager
import json

load_dotenv()

app = Flask(__name__)



secret_name = os.getenv("SECRET_NAME")
project_id = os.getenv("PROJECT_ID")

name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"

client = secretmanager.SecretManagerServiceClient()

response = client.access_secret_version(name=name)
secret_data = response.payload.data.decode("UTF-8")

# Google Sheets setup
#creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "/app/credentials.json")
#print(creds_path)

credentials_path="credentials.json"

with open(credentials_path, "w") as f:
    f.write(secret_data)

#TRY THIS FRIDAY
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.abspath(credentials_path)
#TRY THIS FRIDAY
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
client = gspread.authorize(creds)


# Access the spreadsheet by key
spreadsheet_key = "1nc4ZbHfiJyCkXNuUe_WhsMVTNfrwoYaPcGLH5JE2Xiw"
sheet = client.open_by_key(spreadsheet_key).sheet1


@app.route('/response', methods=['GET'])
def response():
    answer = request.args.get('answer')
    app.logger.info(f"received response: answer={answer}")

    if answer:
        try:
        # Append the key and answer to the spreadsheet
            sheet.append_row([answer])
            return "Thank you for your response!"
        except Exception as e:
            return "failed to record response", 500
        
    return "Missing key or answer", 400


@app.route('/test_google_sheets')
def test_google_sheets():
    try:
        sheet.append_row(["Test"])
        return jsonify({"status": "success", "message": "Successfully appended a test row to the sheet."})
    except Exception as e:
        app.logger.error(f"Error during Google Sheets test: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
    

if __name__ == "__main__":
    print("creating port...")
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))

