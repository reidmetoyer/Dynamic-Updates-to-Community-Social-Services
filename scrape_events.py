import requests
from bs4 import BeautifulSoup

def scrape_smh():
    url = 'https://stmargaretshouse.org/events/'

    # Set the header
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }


    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to retrieve the web page. Status code: {response.status_code}")
    else:

        soup = BeautifulSoup(response.content, 'html.parser')


        events_divs = soup.find_all('div', class_='elementor-element elementor-element-ac9d149 elementor-widget elementor-widget-text-editor')


        for event_div in events_divs:
            container = event_div.find('div', class_='elementor-widget-container')
            if container:

                h4_elements = container.find_all('h4')
                h5_elements = container.find_all('h5')
                p_elements = container.find_all('p')


                num_events = min(len(h4_elements), len(h5_elements), len(p_elements))
                events_dict= {}

                for i in range(num_events):
                    
                    event_details = {}
                    event_name = h4_elements[i].get_text(strip=True)
                    event_date = h5_elements[i].get_text(strip=True)
                    

                    # Find the first <p> after the <h5> element for the location
                    location = h5_elements[i].find_next('p').get_text(strip=True)

                    event_details['Date'] = event_date
                    event_details['Location'] = location
                

                    events_dict[event_name] = event_details

                    # Print the extracted information
                    print(f"Event Name: {event_name}")
                    print(f"Date: {event_date}")
                    print(f"Location: {location}")
                    print('---')

                print(events_dict)

    return events_dict