from typing import List, Tuple
import csv
import requests
import sys
import os

def get_event_podium(competition_id: str, event_id: str) -> Tuple[List[str], str]:
    event_api_url = f'https://www.worldcubeassociation.org/api/v0/competitions/{competition_id}/results/{event_id}'
    response_json = requests.get(event_api_url).json()
    rounds = response_json.get('rounds', [])

    if len(rounds) >= 1:
        return list(map(lambda r: r.get('wca_id'), rounds[0].get('results', [])[:3])), response_json.get('name')
    return [], ""

def get_events_list(competition_id: str) -> List[str]:
    wcif_url = f'https://www.worldcubeassociation.org/api/v0/competitions/{competition_id}/wcif/public'
    response_json = requests.get(wcif_url).json()
    events = response_json.get('events', [])
    return list(map(lambda e: e.get('id'), events))

def get_wca_ids_to_emails(filename: str) -> dict:
    with open(filename, 'r') as csv_file:
        return { r['WCA ID']: r['Email'] for r in csv.DictReader(csv_file) }

def print_help_and_exit():
    print('Usage: python main.py <input_file.csv> <competition_id> <output_file.csv> <1st_prize> <2nd_prize> <3rd_prize>')
    print('Example: python main.py Competition2023-registration.csv Competition2023 Competition2023-winners.csv 15 10 5')
    sys.exit()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('❌ ERROR: Missing input CSV filename parameter.')
        print_help_and_exit()

    if len(sys.argv) < 3:
        print('❌ ERROR: Missing competition ID parameter.')
        print_help_and_exit()

    if len(sys.argv) < 4:
        print('❌ ERROR: Missing competition ID parameter.')
        print_help_and_exit()

    if len(sys.argv) < 7:
        print('❌ ERROR: Missing prize amount(s).')
        print_help_and_exit()

    for help_flag in ['help', '--help', 'h', '-h']:
        if help_flag in sys.argv:
            print_help_and_exit()

    input_csv_filename = sys.argv[1]
    competition_id = sys.argv[2]
    output_csv_filename = sys.argv[3]

    prizes = (sys.argv[4], sys.argv[5], sys.argv[6])

    if os.path.isfile(output_csv_filename):
        os.remove(output_csv_filename)

    wca_ids_to_emails = get_wca_ids_to_emails(input_csv_filename)
    events = get_events_list(competition_id)

    with open(output_csv_filename, 'w') as output_csv_file:
        writer = csv.DictWriter(output_csv_file, ['event', '1st email', '1st prize ($)', '2nd email', '2nd prize ($)', '3rd email', '3rd prize ($)'])
        writer.writeheader()

        for event in events:
            winner_wca_ids, event_name = get_event_podium(competition_id, event)
            first, second, third = list(map(lambda id: wca_ids_to_emails.get(id), winner_wca_ids))
            writer.writerow({ 
                'event': event_name, 
                '1st email': first,
                '1st prize ($)': prizes[0],
                '2nd email': second, 
                '2nd prize ($)': prizes[1],
                '3rd email': third,
                '3rd prize ($)': prizes[2],
            })
