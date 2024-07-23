import os
from flask import Flask, request, jsonify
import gspread
from google.oauth2 import service_account
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
from google.cloud import secretmanager
import json
from datetime import datetime
#from email_notifs import get_sheet_key


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

def get_custom_env_var():
    keyclient = secretmanager.SecretManagerServiceClient()
    project_id = os.getenv('PROJECT_ID')
    secret_id = "ORG_SHEET_KEY"

    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = keyclient.access_secret_version(name=name)
    spreadsheet_key = response.payload.data.decode('UTF-8')
    return spreadsheet_key


@app.route('/track_click')
def track_click():
    spreadsheet_key = get_custom_env_var()
    sheet = client.open_by_key(spreadsheet_key)

    answer = request.args.get('answer')
    recipient_email = request.args.get('recipient_email')
    date = datetime.now().strftime("%Y-%m-%d")

    sheet_name = request.args.get('sheet', 'Sheet1')

    app.logger.info(f"received responseL answer={answer}, sheet={sheet_name}")

    cur_sheet = get_sheet_by_name(sheet_name)
    next_row = len(cur_sheet.col_values(2)) + 1

    if not cur_sheet:
        return "sheet not found", 400

    if sheet_name == "Events":
            event = request.args.get('event')
            cur_sheet.update_cell(next_row, 1, event)
            cur_sheet.update_cell(next_row, 2, answer)
            cur_sheet.update_cell(next_row, 3, recipient_email)
            cur_sheet.update_cell(next_row, 4, date)
            return "Thank you for your response!"

    if answer:
        try:
            cur_sheet.update_cell(next_row, 1, answer)
            cur_sheet.update_cell(next_row, 2, recipient_email)
            cur_sheet.update_cell(next_row, 3, date)
            return "Thank you for your response!"
        except Exception as e:
            return "failed to record response", 500
        
    return "Missing answer", 400


@app.route('/no_response')
def no_response():
    sheet = request.args.get('sheet')
    recipient_email = request.args.get('recipient_email')
    
    html_content = f"""
    <html>
    <head>
        <title>Provide Correct Information</title>
    </head>
    <body>
        <form action="/submit_correct_info" method="post">
            <input type="hidden" name="sheet" value="{sheet}">
            <input type="hidden" name="recipient_email" value="{recipient_email}">
            <label for="correct_info">Please provide the correct information:</label>
            <textarea id="correct_info" name="correct_info" rows="4" cols="50"></textarea>
            <button type="submit">Submit</button>
        </form>
    </body>
    </html>
    """
    return html_content

@app.route('/submit_correct_info', methods=['POST'])
def submit_correct_info():
    sheet_name = request.form['sheet']
    recipient_email = request.form['recipient_email']
    correct_info = request.form['correct_info']
    date = datetime.now().strftime("%Y-%m-%d")

    cur_sheet = get_sheet_by_name(sheet_name)

    if not cur_sheet:
        return "Sheet not found", 400

    next_row = len(cur_sheet.col_values(2)) + 1

    try:
        cur_sheet.update_cell(next_row, 1, 'no')
        cur_sheet.update_cell(next_row, 2, recipient_email)
        cur_sheet.update_cell(next_row, 3, date)
        cur_sheet.update_cell(next_row, 4, correct_info)
        return "Thank you for your response!"
    except Exception as e:
        app.logger.error(f"Failed to record response: {e}")
        return "Failed to record response", 500


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

