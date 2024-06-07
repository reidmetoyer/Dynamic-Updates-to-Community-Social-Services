from bs4 import BeautifulSoup
import requests
import re
from dateutil import parser
import datetime


    

            
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
}


SMH = requests.get("https://stmargaretshouse.org/events/", headers = headers)
soup = BeautifulSoup(SMH.text, "html.parser")

rejectList = ["EVENTS", "Events", "EVENT", "Event", "events", "event"]
eventsList = []
eventsDict = {}
currentTime = datetime.datetime.now()
date = str(currentTime.month) + "-" + str(currentTime.day) + "-" + str(currentTime.year)


# Define regular expression patterns for various date formats
date_patterns = [
    r'\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b',            # Matches 03/14/2024, 05-06-2023, etc.
    r'\b(?:\w+\s\d{1,2}\w{0,2},?\s\d{4})\b',                # Matches January 23rd, 2023
    r'\b\w+\s\d{1,2}\w{0,2}\b',              
]

# Function to extract dates from text
def extractDates(text):
    dates = []
    for pattern in date_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            try:
                parsed_date = parser.parse(match)
                dates.append(parsed_date.strftime('%Y-%m-%d'))
            except parser.ParserError:
                continue
    return dates


#find all header tags
eventHeaders = soup.findAll(["h1", "h2", "h3"])



def isValidEvent(text):
    text = text.lower()
    for word in rejectList:
        if word in text:
            return False
    return True

#find all valid events
for header in eventHeaders:
    headerText = header.getText(strip=True)
    if isValidEvent(headerText):
        paragraphs = []
        nextSibling = header.findNextSibling()

        while nextSibling and nextSibling.name not in ["h1", "h2", "h3"]:
            if nextSibling.name == 'p'or nextSibling.name == "div":
                paragraphs.append(nextSibling.getText(strip=True))
            nextSibling = nextSibling.findNextSibling()
        
        combinedParagraphs = ' '.join(paragraphs)

        #extract dates
        dates = extractDates(combinedParagraphs)

        eventsDict[headerText] = {
            'text': combinedParagraphs,
            'dates': dates
        }


#email info
to = "rmetoye2@nd.edu"
subject = "SMH Scraper Info"
body = ""


for header, content in eventsDict.items():
    body+= f"Header:  {header}"
    body+= f"Info: {content['text']}"
    body+= f"Date: {content['dates']}"






for header, content in eventsDict.items():
    print(f"Header: {header}")
    print(f"Info: {content['text']}")
    print(f"Date: {content['dates']}")
   
    
    print()

print(f"Current date: {date}")
print()   