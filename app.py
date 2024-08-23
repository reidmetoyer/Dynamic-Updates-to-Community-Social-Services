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

#environment variables
load_dotenv()
#start application
app = Flask(__name__)


#setting up secret variables and retrieving secrets
secret_name = os.getenv("SECRET_NAME")
project_id = os.getenv("PROJECT_ID")

name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"

client = secretmanager.SecretManagerServiceClient()

response = client.access_secret_version(name=name)
secret_data = response.payload.data.decode("UTF-8")



credentials_path="credentials.json"

with open(credentials_path, "w") as f:
    f.write(secret_data)


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.abspath(credentials_path)


#initializes google spreadsheet client
def initialize_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
    return gspread.authorize(creds)
    #client = gspread.authorize(creds)


    # Access the spreadsheet by key
    #spreadsheet_key = "1nc4ZbHfiJyCkXNuUe_WhsMVTNfrwoYaPcGLH5JE2Xiw"
    #sheet = client.open_by_key(spreadsheet_key)


#opens a google worksheet based on the sheet_name passed to this function from the HTML buttons in email_notifs
def get_sheet_by_name(sheet, sheet_name):
    try:
        cur_sheet = sheet.worksheet(sheet_name)
        return cur_sheet
    except gspread.WorksheetNotFound:
        app.logger.error(f"Sheet '{sheet_name}' not found.")
        return None


#not required but present
def get_custom_env_var():
    keyclient = secretmanager.SecretManagerServiceClient()
    project_id = os.getenv('PROJECT_ID')
    secret_id = "ORG_SHEET_KEY"

    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = keyclient.access_secret_version(name=name)
    spreadsheet_key = response.payload.data.decode('UTF-8')
    return spreadsheet_key


#self explanatory; 'org' is found in the http response from the html buttons
def get_key_by_org(org):
    if org == 'smh':
            spreadsheet_key = "1nc4ZbHfiJyCkXNuUe_WhsMVTNfrwoYaPcGLH5JE2Xiw"
    elif org == "olotr":
            spreadsheet_key = "1Hr1pnFSiMLi5heVjCGzSTfl-TovPEXFTYdC50MG4h3U"
    elif org == "cfth":
            spreadsheet_key = "1bv6ng14X7A6-sHjOrpt92fzEJ7Reu_WsDjKzx1yw5Zc"
    elif org == "fb":
            spreadsheet_key = "1NzOlYVwSoTyl2_3LbcXAeHtXqXr11iFzvNqXbiLbWDU"
    return spreadsheet_key


#app route for when 'yes' button is pressed
@app.route('/track_click')
def track_click():
    #spreadsheet_key = get_custom_env_var()
    client = initialize_gspread_client()
    #sheet = client.open_by_key(spreadsheet_key)
    info = request.args.get('info')
    answer = request.args.get('answer')
    recipient_email = request.args.get('recipient_email')
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    org = request.args.get('org')

    spreadsheet_key = get_key_by_org(org)
    sheet = client.open_by_key(spreadsheet_key)

    sheet_name = request.args.get('sheet', 'Sheet1')

    app.logger.info(f"received responseL answer={answer}, sheet={sheet_name}")

    cur_sheet = get_sheet_by_name(sheet, sheet_name)
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
            cur_sheet.update_cell(next_row, 1, info)
            cur_sheet.update_cell(next_row, 2, answer)
            cur_sheet.update_cell(next_row, 3, recipient_email)
            cur_sheet.update_cell(next_row, 4, date)
            return "Thank you for your response!"
        except Exception as e:
            return "failed to record response", 500
        
    return "Missing answer", 400


#app route for when 'no' button is pressed
@app.route('/no_response')
def no_response():
    
    info = request.args.get('info')
    org = request.args.get('org')
    sheet_name = request.args.get('sheet')
    recipient_email = request.args.get('recipient_email')
    
    
    html_content = f"""
    <html>
    <head>
        <title>Provide Correct Information</title>
    </head>
    <body>
        <form action="/submit_correct_info" method="post">
            <input type="hidden" name="info" value="{info}">
            <input type="hidden" name="org" value="{org}">
            <input type="hidden" name="sheet_name" value="{sheet_name}">
            <input type="hidden" name="recipient_email" value="{recipient_email}">
            <label for="correct_info">Please provide the correct information:</label>
            <textarea id="correct_info" name="correct_info" rows="4" cols="50"></textarea>
            <button type="submit">Submit</button>
        </form>
    </body>
    </html>
    """
    return html_content

#app route for when user submits correct info after 'no' is pressed
@app.route('/submit_correct_info', methods=['POST'])
def submit_correct_info():

    client = initialize_gspread_client()

    info = request.form['info']
    org = request.form['org']
    sheet_name = request.form['sheet_name']
    recipient_email = request.form['recipient_email']
    correct_info = request.form['correct_info']
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    spreadsheet_key = get_key_by_org(org)
    sheet = client.open_by_key(spreadsheet_key)

    #sheet_name = request.args.get('sheet', 'Sheet1')

    cur_sheet = get_sheet_by_name(sheet, sheet_name)

    if not cur_sheet:
        return "Sheet not found", 400

    next_row = len(cur_sheet.col_values(2)) + 1

    try:
        cur_sheet.update_cell(next_row, 1, info)
        cur_sheet.update_cell(next_row, 2, 'no')
        cur_sheet.update_cell(next_row, 3, recipient_email)
        cur_sheet.update_cell(next_row, 4, date)
        cur_sheet.update_cell(next_row, 5, correct_info)
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
    

#runs application
if __name__ == "__main__":
    print("creating port...")
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))

