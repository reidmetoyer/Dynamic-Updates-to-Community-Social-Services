from openai import OpenAI, AssistantEventHandler
from dotenv import load_dotenv
from email.message import EmailMessage
from dotenv import load_dotenv
import os
from pathlib import Path
import pdfkit

path_to_wkhtmltopdf = '/usr/local/bin/wkhtmltopdf'
config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
client = OpenAI()

#main function to notify smh
def notif_smh():
    #smh-specific variables
    recipient = ""
    urls = ["https://stmargaretshouse.org/contact-us/"]
    file_paths = ["file1.pdf"]

    #notification logic
    pdfs = pdf_download(urls, file_paths)
    info = get_info(pdfs)
    send_email(recipient, info)


    print("notifying st margarets house")

#helper function to download necessary pdfs
def pdf_download(urls, file_paths):
    for file, url in zip(file_paths, urls):
        pdfkit.from_url(url, file, configuration=config)
    return file_paths

#helper function to extract info using chatgpt
def get_info(pdfs):
    info = []
    print("getting info")
    return info

#helper function to construct and send email to target organization
def send_email(recipient, info):
    print("constructing email")
    print("sending email")

notif_smh()
