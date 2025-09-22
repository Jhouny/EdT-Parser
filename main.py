import re
from bs4 import BeautifulSoup
import sys
import bs4
from Event import Event as CustomEvent
from datetime import datetime
import zoneinfo
from ics import Calendar, Event

"""
README:
    > This script parses an HTML file containing a timetable and extracts events into Event objects.
    > Each event includes title, start time, end time, date, location, and description (prof. name usually).

    1. To use this, first go to your EdT page and save the HTML file locally
    2. Change the EDT_FILE variable to point to your saved HTML file
    3. Change the IF_GROUP variable to match your group (1 for IF1, 2 for IF2, etc.)
    4. Run the script: python main.py [optional_path_to_html_file]
"""

EDT_FILE = 'EdT - 4IF@ADE.html'  # Default HTML file path
IF_GROUP = 1 # Change this to 2 for IF2, 3 for IF3, etc.

def approx_time(table: bs4.element.Tag, event: bs4.element.Tag) -> str:
    """
    This function approximates the ending time of an event based on its column span and the tables' time slots.
    """
    total_cols = int(event.attrs['id'].split('-')[-2]) + int(event.attrs['colspan'])
    ind = 2  # Skips the first two <th> elements which are not time slots
    th = table.find('tr', class_='header').find_all('th')[ind]
    summ = int(th.attrs.get('colspan', 1))
    while summ < total_cols:
        ind += 1
        th = table.find('tr', class_='header').find_all('th')[ind]
        summ += int(th.attrs.get('colspan', 1))

    if summ == total_cols:
        end_time = th.text.strip().split('-')[1] + '00'
    else:
        try:
            end_time = table.find('tr', class_='header').find_all('th')[ind-1].text.strip().split('-')[1]
        except IndexError:
            delta = summ - total_cols
            add = 60 - 15*delta
            end_time = table.find('tr', class_='header').find_all('th')[ind-2].text.strip().split('-')[1] + str(add)

    return end_time


def parse_html(file_path: str) -> list[CustomEvent]:
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
    
    events = []
    for day in soup.find_all('tr', class_=f"row-group-{IF_GROUP}"):

        # construct date from day/month/year string
        html_date_content = day.contents[1].get_text()
        date_str = re.search(r'(\d{2}/\d{2}/\d{4})', html_date_content).group(1)

        daily_events = day.find_all('td', class_=['Slot-EDT', 'Slot-CM', 'Slot-TP', 'Slot-TD'])
        for event in daily_events:
            week_table = daily_events[0].parent.parent.parent
            title = event.find_all('td')[0].text.strip()
            
            stime = re.search(r'\d{2}h\d{2}', event.text).group(0)
            start_time = datetime.strptime(f"{date_str} {stime.replace('h', ':')}", '%d/%m/%Y %H:%M').replace(tzinfo=zoneinfo.ZoneInfo('Europe/Paris'))
            
            etime = approx_time(week_table, event)
            end_time = datetime.strptime(f"{date_str} {etime.replace('h', ':')}", '%d/%m/%Y %H:%M').replace(tzinfo=zoneinfo.ZoneInfo('Europe/Paris'))

            try:
                location = event.find_all('td')[1].text.strip().split('\xa0')[1]
            except IndexError:
                location = None

            try:
                description = " ".join(event.find_all('td')[2].text.strip().split('\xa0'))
            except IndexError:
                description = None

            events.append(CustomEvent(title, start_time, end_time, location, description))

    return events

def dump_ics(events: list[CustomEvent], output_file: str):
    calendar = Calendar()
    for event in events:
        ics_event = Event()
        ics_event.name = event.title
        ics_event.begin = event.start_time
        ics_event.end = event.end_time
        ics_event.location = event.location
        ics_event.description = event.description
        calendar.events.add(ics_event)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(calendar.serialize_iter())

if __name__ == '__main__':
    html_file = EDT_FILE  # Default file path if none provided
    if sys.argv[1:]:
        html_file = sys.argv[1]

    events = parse_html(html_file)

    dump_ics(events, 'timetable.ics')
    print(f"Extracted {len(events)} events and saved to 'timetable.ics'")

    
