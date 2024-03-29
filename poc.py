import requests
from bs4 import BeautifulSoup
import json
import pprint
import re
import time
import requests_cache

BASE_URL    = "https://www.espn.com/mens-college-basketball/team/{schedule,roster}/_/id/{team_id}/season/{year}"
GAME_URL    = "https://www.espn.com/mens-college-basketball/game/_/gameId/401258866"
PBP_URL     = "https://www.espn.com/mens-college-basketball/playbyplay/_/gameId/401369935"
SCH_URL     = "https://www.espn.com/mens-college-basketball/team/schedule/_/id/228/season/2022"
RST_URL     = "https://www.espn.com/mens-college-basketball/team/roster/_/id/228/season/2020"

SCH_B_URL   = "https://www.espn.com/mens-college-basketball/team/schedule/_/id/{}/season/{}" # team_id, year
PBP_B_URL     = "https://www.espn.com/mens-college-basketball/playbyplay/_/gameId/{}" # game_id
TEAMS_URL   = "https://www.espn.com/mens-college-basketball/teams"

VERBOSE = False

requests_cache.install_cache("espn_api", backend="sqlite", expire_after=30*86400) # expire after 30 days

def get_request(url):
    try:
        r = requests.get(url)
        while r.status_code == 503:
            time.sleep(1)
            r = requests.get(url)

        return r
    except:
        return get_request(url)

def get_teams():
    with requests_cache.disabled():
        r = get_request(TEAMS_URL)

    soup = BeautifulSoup(r.content, 'html5lib')
    table = soup.findAll('div', attrs={'class': 'mt7'})
    all_teams_by_conference = {}

    for conference in table:
        name = conference.find('div', attrs={'class': 'headline headline pb4 n8 fw-heavy clr-gray-01'})
        name = name.get_text()
        all_teams_by_conference[name] = []

        teams = conference.findAll('div', attrs={'class': 'pl3'})
        for team in teams:
            team_a = team.find('a')
            team_url_split = team_a['href'].split('/')
            team_dict = {
                'name': team_a.get_text(),
                'id': team_url_split[team_url_split.index('id') + 1]
            }

            all_teams_by_conference[name].append(team_dict)

    if VERBOSE:
        pprint.pprint(all_teams_by_conference)

    return all_teams_by_conference

def get_schedule(team_id, year):
    with requests_cache.disabled():
        r = get_request(SCH_B_URL.format(team_id, year))

    soup = BeautifulSoup(r.content, 'html5lib')
    raw_games = soup.find_all('div', attrs={'class': 'flex items-center opponent-logo'})
    schedule = []

    for raw_game in raw_games:
        sections = raw_game.parent.parent.find_all('td', attrs={'class': 'Table__TD'})
        raw_game_span = raw_game.find_all('span')
        span_a = raw_game_span[-1].find('a')
        opp_id = span_a['href'].split('/')[-1] if span_a else None

        game_a = sections[2].find('a')
        results_span = sections[2].find_all('span')

        game_dict = {
            'location': 'Home' if raw_game_span[0].get_text() == 'vs' else 'Away',
            'opponent': {
                'name': raw_game_span[-1].get_text().strip(),
                'id': opp_id
            },
            'date': sections[0].get_text(),
            'id': game_a['href'].split('/')[-1] if game_a else -1
        }

        if not results_span or len(results_span) == 1:
            game_dict['result'] = None
            game_dict['score'] = None
        else:
            game_dict['result'] = results_span[0].text
            game_dict['score'] = results_span[1].text.strip()

        schedule.append(game_dict)

    if VERBOSE:
        pprint.pprint(schedule)

    return schedule

def get_action_from_play(action_text):
    player = None
    action = None
    assist = None

    if 'Official TV Timeout' in action_text:
        action = 'Official TV Timeout'
    elif action_text.startswith('End of'):
        action = action_text.strip()

    elif action_text == 'null':
        return player, action, assist

    elif 'made Three Point Jumper' in action_text:
        action = 'made Three Point Jumper'
        player = action_text.split(action)[0].strip()
    elif 'missed Three Point Jumper' in action_text:
        action = 'missed Three Point Jumper'
        player = action_text.split(action)[0].strip()
    elif 'made Jumper' in action_text:
        action = 'made Jumper'
        player = action_text.split(action)[0].strip()
    elif 'missed Jumper' in action_text:
        action = 'missed Jumper'
        player = action_text.split(action)[0].strip()
    elif 'made Two Point Tip Shot' in action_text:
        action = 'made Two Point Tip Shot'
        player = action_text.split(action)[0].strip()
    elif 'missed Two Point Tip Shot' in action_text:
        action = 'missed Two Point Tip Shot'
        player = action_text.split(action)[0].strip()
    elif 'made Layup' in action_text:
        action = 'made Layup'
        player = action_text.split(action)[0].strip()
    elif 'missed Layup' in action_text:
        action = 'missed Layup'
        player = action_text.split(action)[0].strip()
    elif 'made Free Throw' in action_text:
        action = 'made Free Throw'
        player = action_text.split(action)[0].strip()
    elif 'missed Free Throw' in action_text:
        action = 'missed Free Throw'
        player = action_text.split(action)[0].strip()
    elif 'made Dunk' in action_text:
        action = 'made Dunk'
        player = action_text.split(action)[0].strip()
    elif 'missed Dunk' in action_text:
        action = 'missed Dunk'
        player = action_text.split(action)[0].strip()
    elif 'Turnover' in action_text:
        action = 'Turnover'
        player = action_text.split(action)[0].strip()
    elif 'Steal' in action_text:
        action = 'Steal'
        player = action_text.split(action)[0].strip()
    elif 'Block' in action_text:
        action = 'Block'
        player = action_text.split(action)[0].strip()
    elif 'Offensive Rebound' in action_text:
        action = 'Offensive Rebound'
        player = action_text.split(action)[0].strip()
    elif 'Defensive Rebound' in action_text:
        action = 'Defensive Rebound'
        player = action_text.split(action)[0].strip()
    elif 'Deadball Team Rebound' in action_text:
        action = 'Deadball Team Rebound'
        player = action_text.split(action)[0].strip()
    elif 'Timeout' in action_text:
        action = 'Timeout'
        player = action_text.split(action)[0].strip()
    elif 'Jump Ball' in action_text:
        action = 'Jump Ball'
        player = action_text.split(action)[-1].strip()
    elif 'Foul on' in action_text:
        action = 'Foul'
        player = action_text.split('Foul on')[-1].strip()

    #else:
    #    print(f"{action_text} not handled")
    #    raise Exception

    if 'Assisted by' in action_text:
        assist = action_text.split('Assisted by')[-1].strip()[:-1]

    return player, action, assist

def get_plays(game_id):
    r = get_request(PBP_B_URL.format(game_id))

    soup = BeautifulSoup(r.content, 'html5lib')
    home_name = soup.find('div', attrs={'class': 'team home'})
    home1 = home_name.find('span', attrs={'class': 'long-name'}).text
    home2 = home_name.find('span', attrs={'class': 'short-name'}).text

    away_name = soup.find('div', attrs={'class': 'team away'})
    away1 = away_name.find('span', attrs={'class': 'long-name'}).text
    away2 = away_name.find('span', attrs={'class': 'short-name'}).text

    raw_halves = soup.find_all('div', attrs={'id': re.compile('gp-quarter*')})
    plays = []
    for half_num, raw_half in enumerate(raw_halves):
        raw_plays = raw_half.find('tbody').find_all('tr')
        half_num += 1 # 1-indexing instead of 0-indexing
        for raw_play in raw_plays:
            play = {}
            play_cols = raw_play.find_all('td')
            play['time'] = play_cols[0].get_text()
            play['period'] = half_num
            (player, action, assist) = get_action_from_play(play_cols[2].get_text())
            play['actor'] = player
            play['action'] = action
            play['assist'] = assist
            away_score, home_score = map(int, play_cols[3].text.split(' - '))
            play['away_score'] = away_score
            play['home_score'] = home_score

            plays.append(play)

    if VERBOSE:
        pprint.pprint(plays)

    return plays, ' '.join([home1, home2]), ' '.join([away1, away2])

def get_roster():
    r = get_request(RST_URL)
    soup = BeautifulSoup(r.content, 'html5lib')

    roster = []
    raw_players = soup.find_all('tr', attrs={'class': 'Table__TR Table__TR--lg Table__even'})

    for raw_player in raw_players:
        player_cols = raw_player.find_all('td', attrs={'class':'Table__TD'})
        roster.append({
            'name': player_cols[1].find('a').get_text(),
            'number': player_cols[1].find('span').get_text(),
            'position': player_cols[2].get_text(),
            'height': player_cols[3].get_text(),
            'weight': player_cols[4].get_text(),
            'class': player_cols[5].get_text()
        })

    if VERBOSE:
        pprint.pprint(roster)

    return roster

###         ###
# Main Runner #
###         ###
if __name__ == '__main__':
    #sch = get_schedule(228, 2022)
    # get_roster()
    #res = get_plays(401369133)
    calculate = True
    year = 2017
    print(f"Calculating for {year - 1}-{year}")

    if calculate:
        get_teams_call = get_teams()
        teams = [team for conf in get_teams_call for team in get_teams_call[conf]]
        results = []
        all_blown = []
        for team_num, team in enumerate(teams):
            print(team['name'], team_num)
            schedule = get_schedule(team['id'], year)
            team_report = {
                'id': team['id'],
                'name': team['name'],
                'deltas': [],
            }
            for game in schedule:
                if game['result'] == 'L':

                    pbp, home, away = get_plays(game['id'])
                    if team['name'] == home:
                        home_modifier = 1
                        away_modifier = -1
                    else:
                        home_modifier = -1
                        away_modifier = 1

                    if len(pbp) == 0:
                        print("skipping", game['id'])
                        continue

                    score_delta = []
                    for play in pbp:
                        h = play['home_score']
                        a = play['away_score']
                        score_delta.append({
                            'delta': h * home_modifier + a * away_modifier,
                            'home_score': h,
                            'away_score': a
                        })

                    team_report['deltas'].append({
                        'home_team': home,
                        'away_team': away,
                        'situation': max(score_delta, key=lambda x: x['delta']),
                        'gameid': game['id']
                    })

            if len(team_report['deltas']) == 0:
                team_report['worst_delta'] = 0
                team_report['worst_gameid'] = 0
                continue
            else:
                worst = max(team_report['deltas'], key=lambda x: x['situation']['delta'])
                worst_index = team_report['deltas'].index(worst)
                team_report['worst_situation'] = worst

            results.append(team_report)
            all_blown.extend(team_report['deltas'])

        with open(f"{year - 1}-{year}-3.json", "w") as fp:
            json.dump(results, fp)

        worst_loss = sorted(all_blown, key=lambda x: x['situation']['delta'], reverse=True)
        print("WORST BLOWN LEAD")
        for i, g in enumerate(worst_loss[:10]):
            print(f"{i + 1} - {g['situation']['delta']} ({g['away_team']} {g['situation']['away_score']} - {g['situation']['home_score']} {g['home_team']})")
        print()

        avg_largest_margin = sorted(results, key=lambda x: sum(y['situation']['delta'] for y in x['deltas']) / len(x['deltas']), reverse=True)
        print("AVERAGE BLOWN LEAD")
        for i, g in enumerate(avg_largest_margin[:20]):
            print(i + 1, '-', g['name'], f"{sum(y['situation']['delta'] for y in g['deltas']) / len(g['deltas']):.2f}", f"out of {len(g['deltas'])} games")
        print()

# worst_loss = sorted(results, key=lambda x: x['worst_delta']['delta'], reverse=True)
# avg_largest_margin = sorted(results, key=lambda x: sum(y['delta'] for y in x['deltas'])/len(x['deltas']), reverse=True)
# biggest_losers = avg_largest_margin[:20]
# for index, team in enumerate(sorted(biggest_losers, key=lambda x: sum(y['delta'] > 0 for y in x['deltas'])))