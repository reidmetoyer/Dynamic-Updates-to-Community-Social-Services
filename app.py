import os
from flask import Flask, request
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("servacccreds.json", scope)
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
