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

app = Flask(__name__)

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("/Users/reidmetoyer/Downloads/credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Responses").sheet1

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
    send_email(org, recipient, info)
    file_paths.append(output_pdf)
    #delete_pdfs(file_paths)


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
def send_email(org, recipient, info):
    print("constructing email")
    print(info)
    #subject = org + " Website Info Check-In"
    body = "Here's your regularly scheduled website information check-in. Take a look at what we've identified on your website, and make sure all the information is correct. If it's not, make note of it and try to fix it as soon as you can!\n\n"

    for item in info:
        if item == "events":
            body += "\nYour website lists "
            for event in info[item]:
                body += event + ", " 
            body += "as upcoming. Is this correct? Yes/No\n"
            body += "-------------------\n\n"
        elif item == "hours of operation":
            body += "Your hours of operation are " + info[item] + ". Is this correct? Yes/No\n"
            body += "-------------------\n"
        else:
            body += "Your " + item + " is " + info[item] + ". Is this correct? Yes/No\n"
            body += "-------------------\n"




    body = """\
    <html>
      <body>
        <p>Is this information up to date?<br>
           <a href="https://silent-ears-wish.loca.lt/response?answer=yes">Yes</a><br>
           <a href="https://silent-ears-wish.loca.lt/response?answer=no">No</a>
        </p>
      </body>
    </html>
    """
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = "Website Info Check-In"
    msg.attach(MIMEText(body, 'html'))
   #msg.set_content(body)
    context = ssl.create_default_context()


    print("sending email")
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender, email_password)
        server.sendmail(sender, recipient, msg.as_string())

    print(body)

def response():
    answer = request.args.get('answer')
    sheet.append_row([answer])
    return "Thank you for your response!"


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

notif_smh()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=7030)


#notif_olotr()
#notif_cfth()
