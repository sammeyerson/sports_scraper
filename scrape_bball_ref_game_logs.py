import sys, os
import time
import pandas as pd
from bs4 import BeautifulSoup
import requests
import unidecode

request_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.2) AppleWebKit/536.2.2 (KHTML, like Gecko) Chrome/25.0.807.0 Safari/536.2.2'
}

def scrape_all_names(url):
    page = requests.get(url, headers= request_headers)
    print(f"STATUS CODE: {page.status_code}")
    if page.status_code == 429:
        print(f"Sleeping, then retrying after: {page.headers['Retry-After']} seconds")
        time.sleep(int(page.headers['Retry-After']))
        scrape_all_names(url)
    soup = BeautifulSoup(page.text, 'lxml')

    table_player_stats = soup.find('table', id='totals_stats')

    player_names = []
    player_teams = []
    player_ids = []
    player_links = []

    year = '2023'

    for row in table_player_stats.find_all('tr')[1:]:

        player_name = row.find('td', attrs={'data-stat': 'player'})

        if player_name is not None:

            player_names.append(unidecode.unidecode(player_name.getText()))
            #outputString = unidecode.unidecode(string)
            #player_names.append(player_name.getText())
            player_teams.append(row.find('td', attrs={'data-stat': 'team_id'}).getText())
            player_id = player_name.find('a')['href'].replace('.html', '')
            player_ids.append(player_id)

            player_links.append(f"https://www.basketball-reference.com{player_id}/gamelog/{year}")



    data = {
        'Player': player_names,
        'Team': player_teams,
        'ID': player_ids,
        'Link': player_links
    }
    player_data = pd.DataFrame.from_dict(data)
    player_data = player_data.drop_duplicates(subset = 'Player')
    player_data.to_csv('nba_names.csv')
    return player_data

def scrape_box_scores(player_name_data):
    
    player_ids, player_names, dates, playeds, teams, opponents, game_starteds, mps, fgms, fgas, three_makes, three_attempts, ftms, ftas, \
    orbs, drbs, trbs, asts, stls, blks, tovs, pfs, pts, plus_minuss  = [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []
    

    for index, row in player_name_data.iterrows():
        try:
            time.sleep(4)
            url = row['Link']
            page = requests.get(url, headers= request_headers)
            print(f"Player: {row['Player']}. Status code {page.status_code}")

            if page.status_code == 429:
                print(f"STATUS CODE: {page.status_code}")
                print(f"Retry after: {page.headers['Retry-After']} seconds")
                time.sleep(int(page.headers['Retry-After']))
                page = requests.get(url, headers= request_headers)

            soup = BeautifulSoup(page.text, 'lxml')
            table_player_gamelog = soup.find('table', id='pgl_basic')
            for tr in table_player_gamelog.findAll('tr')[1:]:
                #print(tr)
                cells = tr.findAll('td')
                #print(f"CELLS: {cells}")
                if len(cells) > 0:
                    game_num = cells[0].getText()
                    player_ids.append(row['ID'])
                    player_names.append(row['Player'])
                    dates.append(cells[1].getText())
                    teams.append(cells[3].getText())
                    opponents.append(cells[5].getText())

                    played = True
                    if game_num == '':
                        played = False
                        playeds.append(played)
                        game_starteds.append(-1)
                        mps.append(-1)
                        fgms.append(-1)
                        fgas.append(-1)
                        three_makes.append(-1)
                        three_attempts.append(-1)
                        ftms.append(-1)
                        ftas.append(-1)
                        orbs.append(-1)
                        drbs.append(-1)
                        trbs.append(-1)
                        asts.append(-1)
                        stls.append(-1)
                        blks.append(-1)
                        tovs.append(-1)
                        pfs.append(-1)
                        pts.append(-1)
                        plus_minuss.append(-1)
                    else:
                        playeds.append(played)
                        game_starteds.append(cells[7].getText())
                        minutes_played = cells[8].getText().split(':')
                        seconds_as_decimal = int(minutes_played[1])/60
                        minutes_played = int(minutes_played[0]) + seconds_as_decimal
                        mps.append(minutes_played)
                        fgms.append(int(cells[9].getText()))
                        fgas.append(int(cells[10].getText()))
                        three_makes.append(int(cells[12].getText()))
                        three_attempts.append(int(cells[13].getText()))
                        ftms.append(int(cells[15].getText()))
                        ftas.append(int(cells[16].getText()))
                        orbs.append(int(cells[18].getText()))
                        drbs.append(int(cells[19].getText()))
                        trbs.append(int(cells[20].getText()))
                        asts.append(int(cells[21].getText()))
                        stls.append(int(cells[22].getText()))
                        blks.append(int(cells[23].getText()))
                        tovs.append(int(cells[24].getText()))
                        pfs.append(int(cells[25].getText()))
                        pts.append(int(cells[26].getText()))
                        #print(f"PLUS MINUS: {cells[28]}")
                        if cells[28].getText() == '':
                            plus_minuss.append(int(0))
                        else:
                            plus_minuss.append(str(cells[28].getText()))

        except Exception as e:
            print(f"Exception: {e} occurred")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(f"ERROR: player: {row['Player']}, player ESPN ID:{row['ID']}, INDEX: {index} URL: {url}\ntype: {exc_type}, obj: {exc_obj}, fname: {fname}, tb: {exc_tb.tb_lineno}")

        #if index > 10:
            #break

    data = {
        'ID': player_ids,
        'Name': player_names,
        'Date': dates,
        'Played': playeds,
        'Team': teams,
        'Opponent': opponents,
        'Minutes': mps,
        'FGM': fgms,
        'FGA': fgas,
        '3PM': three_makes,
        '3PA': three_attempts,
        'FTM': ftms,
        'FTA': ftas,
        'ORB': orbs,
        'DRB': drbs, 
        'TRB': trbs,
        'AST': asts,
        'STL': stls,
        'BLK': blks,
        'TOV': tovs, 
        'PF': pfs,
        'PTS': pts,
        'Plus/Minus': plus_minuss
    }
    player_game_logs = pd.DataFrame.from_dict(data)
    print(player_game_logs)
    player_game_logs.to_csv('player_game_logs.csv')
    return player_game_logs
    


def main():
    season = '2023'
    url_all_names = f'https://www.basketball-reference.com/leagues/NBA_{season}_totals.html#totals_stats'
    player_name_data = scrape_all_names(url_all_names)
    print(player_name_data)
    scrape_box_scores(player_name_data)

if __name__ == "__main__":
    main()