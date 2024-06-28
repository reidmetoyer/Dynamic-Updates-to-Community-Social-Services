from bs4 import BeautifulSoup
import requests
import re
from dateutil import parser
from datetime import datetime
from email.message import EmailMessage
import ssl
import smtplib
from openai import OpenAI, AssistantEventHandler
from dotenv import load_dotenv
import os
from pathlib import Path
from typing_extensions import override
from eventextraction import extract_events




env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
client = OpenAI()

sender = 'rmetoye2@nd.edu'
recipients = []


def download_webpage(url, file_path):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
    }

    try:
        response = requests.get(url, headers = headers)
        response.raise_for_status()
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(response.text)
        print(f"Webpage downloaded and saved to {file_path}")
    except requests.RequestException as e:
        print(f"Failed to download the webpage: {e}")

    




"""def scrape_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
    }
    try:
        response = requests.get(url, headers = headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            return str(soup.prettify())
        else:
            return f"Error: Unable to fetch webpage, status code: {response.status_code}"
        
        
    except Exception as e:
        return f"Error: {str(e)}"
"""

url = "https://stmargaretshouse.org/events/"
file_path = 'SMH_page.html'
download_webpage(url, file_path)
#html_content = scrape_page(url)
#print(html_content)

#to-do, requires openai api

#will have to standardized all dates, aka, tell ChatGPT to return dates in form x/y/z or november 22, 2023 etc
def date_logic(events):
    
    cur_date = datetime.now()
    for organization, events_list in events.items():
        for event, details in events_list.items():
            event_date_str = details['date']
            event_date = datetime.strptime(event_date_str, '%B %Y')
            days = (cur_date-event_date).days
            print(event)
            print(days)
            if (days >= 365):
                details['status'] = 'outdated'
            elif 0 < days < 365:
                details['status'] = 'past event'          
            else:
                details['status'] = 'upcoming event'

events = extract_events()
print(events)


def construct_email(events):
    subject = "SSO Organization Update"
    body = "SSO Organization Update\n\n\n"
    

    #events check
    for organization, events_list in events.items():
        
        outdated_events = organization + ": OUTDATED EVENTS\n\n"
        past_events = organization + ": PAST EVENTS\n\n"
        upcoming_events = organization + ": UPCOMING EVENTS\n\n"
        
        for event, details in events_list.items():
            
            status = details['status']
            if status == 'outdated':
                outdated_events += event + " is outdated...\n\n"
            elif status == 'past event':
                past_events += event + " is a past event.\n\n"
            else:
                upcoming_events += event + " is upcoming!\n\n"

        body += outdated_events
        if outdated_events:
            body += "We recommend updating your website to reflect the current status of your events!\n\n\n"
        else:
            body += "Your website is all up to date, great job!"

        body += past_events
        if past_events:
            body += "These events have passed, but may be of interest because they occurred in the last year.\n\n\n"
        
        body += upcoming_events
        if upcoming_events:
            body += "Good luck with your upcoming events! And don't forget to update your website once they've passed!\n\n\n"


    body += "If you have any questions or concerns about the accuracy or functionality of the update program, don't hesitate to email reid.metoyer@gmail.com, and I'll get back to you as soon as possible!\n"
    print(body)

    return body


def send_emails(sender, recipients):
    print(sender)



def delete_htmls():
    print("delete htmls: to do")

date_logic(events)
construct_email(events)
send_emails(sender, recipients)
#print(events)