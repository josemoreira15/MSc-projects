from bs4 import BeautifulSoup
import requests, json
from tqdm import tqdm

BASE_URL = 'https://fbref.com'
LEAGUE_URL = '/pt/comps/32/Primeira-Liga-Estatisticas'
HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}
    
CLUB_DATA = {}

content = requests.get(f"{BASE_URL}{LEAGUE_URL}", headers=HEADERS)
soup = BeautifulSoup(content.text, 'html.parser')

league_table = soup.find("table", attrs={'id': 'results2023-2024321_overall'}).find('tbody').find_all('tr')
    
for elem in league_table:
    team = elem.find('td', attrs={'data-stat': 'team'}).find('a')
    CLUB_DATA[team.text] = {
        'link': team['href'],
        'attendance_per_g': elem.find('td', attrs={'data-stat': 'attendance_per_g'}).text
    }


file = json.load(open('stats_sheet.json'))

RESULTS = {}


for club in tqdm(CLUB_DATA.keys(), desc=f"#Collecting", ascii ='-#'):
    content = requests.get(f"{BASE_URL}{CLUB_DATA[club]['link']}", headers=HEADERS)
    soup = BeautifulSoup(content.text, 'html.parser')

    CLUB_DATA[club]['players'] = {}
    CLUB_DATA[club]['against'] = {}

    table = soup.find('table', attrs={'id': 'stats_standard_32'}).find('tbody').find_all('tr')
    for elem in table:
        player = elem.find('th', attrs={'data-stat': 'player'}).find('a').text
        CLUB_DATA[club]['players'][player] = {}
        
        
    for key, values in file['players'].items():

        table = soup.find('table', attrs={'id': f'{key}'})
        for elem in table.find('tbody').find_all('tr'):
            player = elem.find(f'{values["player_tag"]}', attrs={'data-stat':'player'}).find('a').text

            CLUB_DATA[club]['players'][player][f'{key}'] = {}
            CLUB_DATA[club][f'{key}'] = {}
            CLUB_DATA[club]['against'][f'{key}'] = {}

            player_values = values['players'] + values['team']
            for value in player_values:
                CLUB_DATA[club]['players'][player][f'{key}'][f'{value}'] = elem.find('td', attrs={'data-stat': f'{value}'}).text
    

        team_stats = table.find('tfoot').find_all('tr')[0]
        for value in values['team']:
            CLUB_DATA[club][f'{key}'][f'{value}'] = team_stats.find('td', attrs={'data-stat': f'{value}'}).text

        against_stats = table.find('tfoot').find_all('tr')[1]
        for value in values['team']:
            CLUB_DATA[club]['against'][f'{key}'][f'{value}'] = against_stats.find('td', attrs={'data-stat': f'{value}'}).text
        
           
     ## RESULTS
            

    table = soup.find('table', attrs={'id': 'matchlogs_for'}).find('tbody').find_all('tr')
    for elem in table:
            competition = elem.find('td', attrs={'data-stat': 'comp'}).find('a').text
            if competition == 'Primeira Liga':
                venue = elem.find('td', attrs={'data-stat': 'venue'}).text

                game_id = f"{elem.find('td', attrs={'data-stat': 'opponent'}).find('a').text}_{club}"
                if venue == 'Em casa':
                    game_id = f"{club}_{elem.find('td', attrs={'data-stat': 'opponent'}).find('a').text}"
                
                round = elem.find('td', attrs={'data-stat': 'round'}).text
                RESULTS[round] = RESULTS.get(round, {})
                

                if game_id not in RESULTS[round]:
                    RESULTS[round][game_id] = {'date': elem.find('th', attrs={'data-stat': 'date'}).find('a').text}
                    
                    for value in file['results']['general']:
                        RESULTS[round][game_id][value] = elem.find('td', attrs={'data-stat': f'{value}'}).text
                
                RESULTS[round][game_id][club] = {}
                for value in file['results']['private']:
                    RESULTS[round][game_id][club][value] = elem.find('td', attrs={'data-stat': f'{value}'}).text
                    
                    
    

with open('fbref_clubs.json' ,'w') as file:
    json.dump(CLUB_DATA, file, indent=4, ensure_ascii=False)


with open('fbref_results.json' ,'w') as file:
    json.dump(RESULTS, file, indent=4, ensure_ascii=False)