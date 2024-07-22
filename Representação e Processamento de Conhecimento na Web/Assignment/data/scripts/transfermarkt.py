from bs4 import BeautifulSoup
import requests, json
from tqdm import tqdm

BASE_URL = 'https://www.transfermarkt.pt'
LEAGUE_URL = 'primeira-liga/startseite/wettbewerb/PO1'
HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}

PLAYER_DATA = []

def get_club_urls(year):
    content = requests.get(f"{BASE_URL}/{LEAGUE_URL}/plus/?saison_id={year}", headers=HEADERS)
    soup = BeautifulSoup(content.text, 'html.parser')

    club_data = []

    table = soup.find_all("div", class_="responsive-table")
    for elem in table:
        for item in elem.find_all('td'):
            if ['hauptlink', 'no-border-links'] == item.get('class'):
                club = item.find('a')
                club_data.append({'club': club.text, 'href': club.get('href')})

    return club_data
 

def get_player_urls(year):
    club_urls = get_club_urls(year)

    player_urls = []

    for club_url in tqdm(club_urls, desc=f'Player URLs season={year}', ascii ='-#'):
        content = requests.get(f"{BASE_URL}{club_url['href']}", headers=HEADERS)
        soup = BeautifulSoup(content.text, 'html.parser')

        club_players = []

        table = soup.find_all("table", class_="inline-table")
        for elem in table:
            for item in elem.find_all("a"):
                club_players.append({item.text.strip(): item.get('href')})
        
        player_urls.append({club_url['club']: club_players})

    return player_urls


def get_player_info(year):
    player_urls = get_player_urls(year)

    for club in player_urls:
        for club_name, players in club.items():
            players_data = []
            for player in tqdm(players, desc=f'#{club_name} Player info', ascii ='-#'):
                for player_name, player_url in player.items():
                    player_info = {}

                    content = requests.get(f"{BASE_URL}{player_url}", headers=HEADERS)
                    soup = BeautifulSoup(content.text, 'html.parser')

                    elems = soup.find_all("div", attrs={'class': 'info-table info-table--right-space'})

                    if len(elems) == 0:
                        elems = soup.find_all("div", attrs={'class': 'info-table info-table--right-space min-height-audio'})

                    for elem in elems:
                        info = elem.find_all("span", class_='info-table__content')

                        for i in range(0, len(info), 2):
                            key = info[i].text.strip().strip(':')
                            player_info[key] = info[i + 1].text.strip().replace(u"\u00A0", " ")


                    market_value = soup.find("a", attrs={"class": "data-header__market-value-wrapper"})
                    if market_value:
                        market_value = market_value.text.split(" ")[0].split(',')
                        if len(market_value) == 1:
                            market_value = market_value[0] + ' k'
                        else:
                            market_value = market_value[0] + ' M'
                        player_info['Valor de Mercado'] = market_value

                    elems = soup.find_all("div", attrs={'class': 'tm-player-additional-data'})
                    for elem in elems:
                        clausula = elem.find('div', attrs={'class': 'content'})
                        formacao = elem.find('h2')

                        if clausula and 'Cláusula de rescisão:' in clausula.text:
                            player_info['Cláusula de Rescisão'] = clausula.text.split('Cláusula de rescisão: ')[-1].strip().split('\n')[0].strip()
                        elif formacao and 'Clubes formação' in formacao.text:
                            player_info['Formação'] = elem.find('div', attrs={'class': 'content'}).text.strip().replace('\r\n', ' ')

                players_data.append({player_name: player_info})
        PLAYER_DATA.append({club_name: players_data})
       
        

if __name__ == '__main__':
    get_player_info(2023)

    with(open("transfermarkt.json", "w")) as file:
        json.dump(PLAYER_DATA, file, indent=2, ensure_ascii=False)