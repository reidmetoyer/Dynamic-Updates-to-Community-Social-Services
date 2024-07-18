import os
from flask import Flask, request, jsonify
import gspread
from google.oauth2 import service_account
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
from google.cloud import secretmanager
import json
from datetime import datetime

load_dotenv()

app = Flask(__name__)



secret_name = os.getenv("SECRET_NAME")
project_id = os.getenv("PROJECT_ID")

name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"

client = secretmanager.SecretManagerServiceClient()

response = client.access_secret_version(name=name)
secret_data = response.payload.data.decode("UTF-8")



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
sheet = client.open_by_key(spreadsheet_key)



def get_sheet_by_name(sheet_name):
    try:
        cur_sheet = sheet.worksheet(sheet_name)
        return cur_sheet
    except gspread.WorksheetNotFound:
        app.logger.error(f"Sheet '{sheet_name}' not found.")
        return None


@app.route('/track_click')
def track_click():
    answer = request.args.get('answer')
    recipient_email = request.args.get('recipient')
    date = datetime.now().strftime("%Y-%m-%d")

    next_row = len(sheet.col_values(2)) + 1

    sheet_name = request.args.get('sheet', 'Sheet1')
    app.logger.info(f"received responseL answer={answer}, sheet={sheet_name}")

    cur_sheet = get_sheet_by_name(sheet_name)
    if not cur_sheet:
        cur_sheet = client.open_by_key(spreadsheet_key).sheet1
        sheet.update_cell(next_row, 1, answer)
        sheet.update_cell(next_row, 2, recipient_email)
        sheet.update_cell(next_row, 3, date)


    if answer:
        try:
            cur_sheet = client.open_by_key(spreadsheet_key).sheet1
            sheet.update_cell(next_row, 1, answer)
            sheet.update_cell(next_row, 2, recipient_email)
            sheet.update_cell(next_row, 3, date)
            return "Thank you for your response!"
        except Exception as e:
            return "failed to record response", 500
        
    return "Missing answer", 400


"""
@app.route('/response', methods=['GET'])
def response():
    answer = request.args.get('answer')
    sheet_name = request.args.get('sheet', 'Sheet1')
    app.logger.info(f"received response: answer={answer}, sheet={sheet_name}")

    cur_sheet = get_sheet_by_name(sheet_name)
    if not cur_sheet:
        cur_sheet = client.open_by_key(spreadsheet_key).sheet1
        cur_sheet.append_row(([answer]))
    
    if answer:
        try:
        # Append the key and answer to the spreadsheet
            cur_sheet.append_row([answer])
            return "Thank you for your response!"
        except Exception as e:
            return "failed to record response", 500
        
    return "Missing key or answer", 400
"""

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

