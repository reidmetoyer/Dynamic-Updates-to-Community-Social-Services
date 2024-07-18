from openai import OpenAI, AssistantEventHandler
from dotenv import load_dotenv
from email.message import EmailMessage
from dotenv import load_dotenv
import os
from pathlib import Path
import pdfkit
import PyPDF2
from info_extract import extract_info
import ssl
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Flask, request
import gspread
from oauth2client.service_account import ServiceAccountCredentials
#from app import app, sheet



path_to_wkhtmltopdf = '/usr/local/bin/wkhtmltopdf'
config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)
options = {
    'disable-javascript': '',
    'javascript-delay': 5000,
    'no-stop-slow-scripts': ''
}



env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
client = OpenAI()


sender = "rmetoye2@nd.edu"
recipient = "reid.metoyer@gmail.com"
email_password = "bofw ucqi mvis sskp"




#spreadsheet_key = "1nc4ZbHfiJyCkXNuUe_WhsMVTNfrwoYaPcGLH5JE2Xiw"
#sheet = client.open_by_key(spreadsheet_key).sheet1

#ST MARGARET's HOUSE
def notif_smh():
    #smh-specific variables
    org = "SMH"
    #recipient = ""
    urls = ["https://stmargaretshouse.org/contact-us/", "https://stmargaretshouse.org/events/"]
    file_paths = ["file1.pdf", "file2.pdf"]

    #notification logic
    print("notifying st margarets house")
    output_pdf = "merged_output.pdf"
    pdf_download(urls, file_paths, output_pdf)
    info = get_info(output_pdf)
    send_email(recipient, info)
    file_paths.append(output_pdf)
    delete_pdfs(file_paths)


#OUR LADY OF THE ROAD
def notif_olotr():
    #olotr-specific variables
    org = "OLOTR"
    #recipient = ""
    urls = ["https://www.olrsb.org/get-involved"]
    file_paths = ["file1.pdf"]

    
    #notification logic
    print("notifying our lady of the road")
    output_pdf = "merged_output.pdf"
    pdf_download(urls, file_paths, output_pdf)
    info = get_info(output_pdf)
    send_email(org, recipient, info)
    file_paths.append(output_pdf)
    delete_pdfs(file_paths)


# CENTER FOR THE HOMELESS
def notif_cfth():
    #smh-specific variables
    org = "CFTH"
    #recipient = ""
    urls = ["https://www.cfh.net/contact"]
    file_paths = ["file1.pdf"]

    
    #notification logic
    print("notifying center for the homeless")
    output_pdf = "merged_output.pdf"
    pdf_download(urls, file_paths, output_pdf)
    info = get_info(output_pdf)
    send_email(org, recipient, info)
    file_paths.append(output_pdf)
    delete_pdfs(file_paths)
    

#helper function to download necessary pdfs
def pdf_download(urls, file_paths, output_path):
    #download files
    for file, url in zip(file_paths, urls):
        pdfkit.from_url(url, file, configuration=config, options=options)

    #merge files
    pdf_merger = PyPDF2.PdfMerger()

    for pdf in file_paths:
        pdf_merger.append(pdf)

    with open(output_path, 'wb') as output_file:
        pdf_merger.write(output_file)


#helper function to extract info using chatgpt
def get_info(pdfs):
    info = extract_info()
    print("getting info")
    return info

#helper function to construct and send email to target organization
def construct_email(org, recipient, info):
    print("constructing email")
    print(info)
    #subject = org + " Website Info Check-In"
    body = """
    <html>
    <body>
    <p>Please review the following information and respond:</p>
    <ul>
    """
    
    # Add each item from the dictionary to the body with yes/no forms
    for key, value in info.items():
        body += f"""
        <li>
            <strong>{key}:</strong> {value} <br>
            <form action="https://email-notifs-qbwaylvbsa-uc.a.run.app/track_click" method="get">
                <input type="hidden" name="sheet" value="{key}">
                <input type="hidden" name="recipient_email" value="{recipient}">
                <button type="submit" name="answer" value="yes">Yes</button>
                <button type="submit" name="answer" value="no">No</button>
            </form>
        </li>
        """
    
    body += """
    </ul>
    </body>
    </html>
    """

    return body

def send_email(recipient, info):


    server = smtplib.SMTP(host='smtp.gmail.com', port=587)
    server.starttls()
    server.login(sender, email_password)

    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = "Website Info Check-In"
    body = construct_email('smh', recipient, info)

    msg.attach(MIMEText(body, 'html'))
   #msg.set_content(body)
    context = ssl.create_default_context()


    server.send_message(msg)
    server.quit()



def delete_pdfs(file_paths):
    current_dir = os.getcwd()
    for file in file_paths:
        file_path = os.path.join(current_dir, file)
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Deleted {file}")
            else:
                print(f"File {file} does not exist")
        except Exception as e:
            print(f"Error deleting {file}: {e}")

#notif_smh()
#notif_olotr()
#notif_cfth()
"""
if __name__ == "__main__":
    info_dict = {
        "Name": "John Doe",
        "Email": "john.doe@example.com",
        "Subscription": "Premium"
    }

    server_url = "http://localhost:8080"
    send_email("reid.metoyer@gmail.com", info_dict)
"""

notif_smh()