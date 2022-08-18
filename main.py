import pandas as pd
import numpy as np
import json
import requests


r = requests.get('https://fantasy.premierleague.com/api/bootstrap-static/')
x = r.json()

fpl_team_data = pd.DataFrame(x['teams'])

# fpl_team_data.to_csv("TEAM_DATA_21_22.csv",index=False,header=True)

fpl_players_data = pd.DataFrame(x['elements'])

fpl_players_data['player_name'] = fpl_players_data['first_name'] + " " + fpl_players_data['second_name']

# fpl_players_data.to_csv("PLAYER_DATA_21_22.csv",index=False,header=True)

fpl_players_info = fpl_players_data

fpl_players_info['position'] = 'FWD'

fpl_players_info['position'] = np.select(
    [
        fpl_players_info['element_type'] == 1,
        fpl_players_info['element_type'] == 2,
        fpl_players_info['element_type'] == 3,
        fpl_players_info['element_type'] == 4,
    ],
    [
        'GKP',
        'DEF',
        'MID',
        'FWD'
    ],
    default='FWD'
)

fpl_players_info = fpl_players_info.loc[:,['player_name','id','team','position']]

fpl_players_info.columns = ['player_name','player_id','team_id','position']

fpl_players_info = fpl_players_info.merge(fpl_team_data.loc[:,['id','short_name']], left_on = 'team_id', right_on = 'id', how='left')

del fpl_players_info['id']

fpl_players_info = fpl_players_info.rename(columns={"short_name": "team_name"})

# fpl_players_info.to_csv("PLAYER_INFO_21_22.csv",index=False,header=True)

r_score = requests.get('https://fantasy.premierleague.com/api/element-summary/1/')
x_score = r_score.json()

fpl_players_all_gws_data = pd.DataFrame(x_score['history'])

m = max(fpl_players_data['id'])

for i in range(2,m+1):
    pagex = 'https://fantasy.premierleague.com/api/element-summary/' + str(i) + '/'
    temp_r_score = requests.get(pagex)
    temp_x_score = temp_r_score.json()
    temp_fpl_players_all_gws_data = pd.DataFrame(temp_x_score['history'])
    fpl_players_all_gws_data = pd.concat([fpl_players_all_gws_data,temp_fpl_players_all_gws_data], axis=0)

fpl_players_all_gws_data.reset_index(drop=True)

# fpl_players_all_gws_data.to_csv("PLAYER_ALL_GWS_DATA_21_22.csv",index=False,header=True)

fpl_players_collab = fpl_players_all_gws_data.merge(fpl_players_info, left_on = 'element', right_on = 'player_id', how='left')

fpl_players_collab = fpl_players_collab.merge(fpl_team_data.loc[:,['id','short_name']], left_on = 'opponent_team', right_on = 'id', how='left')

del fpl_players_collab['id']

fpl_players_collab = fpl_players_collab.rename(columns={"short_name": "opponent_name", "total_points": "round_points"})

fpl_player_cols = fpl_players_info.columns.to_list()

fpl_player_cols = fpl_player_cols + ['opponent_name', 'round', 'round_points', 'goals_scored', 'assists',
                                     'clean_sheets', 'own_goals', 'penalties_saved', 'penalties_missed',
                                     'yellow_cards', 'red_cards', 'saves', 'bonus']

fpl_players_collab = fpl_players_collab[fpl_player_cols]

# fpl_players_collab.to_csv("FPL_PLAYERS_COLLAB_DATA_21_22.csv",index=False,header=True)


r_team_id = requests.get('https://fantasy.premierleague.com/api/entry/58575/')
x_team_id = r_team_id.json()

all_leagues = x_team_id['leagues']

classic_leagues = pd.DataFrame(all_leagues['classic'])

classic_league_ids = list(classic_leagues[classic_leagues['league_type'] == 'x'].id)

classic_league_ids = [667096]

all_leagues_data = pd.DataFrame()

for i in classic_league_ids:
    temp_league_string = 'https://fantasy.premierleague.com/api/leagues-classic/' + str(i) + '/standings/'
    r_league = requests.get(temp_league_string)
    x_league = r_league.json()
    league_data = pd.DataFrame(x_league['standings']['results'])
    all_leagues_data = pd.concat([all_leagues_data,league_data], axis=0)

# all_leagues_data = all_leagues_data['entry']

max_gw = np.max(fpl_players_collab['round'])

ids = list(all_leagues_data['entry'].unique())

start_event = x_team_id['started_event']

fpl_players_all_managers_gws_data = pd.DataFrame()

for i in ids:
    manager_string = 'https://fantasy.premierleague.com/api/entry/' + str(i) + '/'
    temp_r_id = requests.get(manager_string)
    temp_x_id = temp_r_id.json()
    if 'started_event' in list(temp_x_id.keys()):
        start_event = temp_x_id['started_event']
    else:
        start_event = 0
    if start_event == 0:
        fpl_players_all_managers_gws_data = fpl_players_all_managers_gws_data
    else:
        if max_gw == 1:
            manager_weekly_string = 'https://fantasy.premierleague.com/api/entry/' \
                                    + str(i) + '/event/' + str(j) + '/picks/'
            temp_r_weekly = requests.get(manager_weekly_string)
            temp_x_weekly = temp_r_weekly.json()
            fpl_manager_data = pd.DataFrame(temp_x_weekly['picks'])
            fpl_manager_data['gw'] = j
            fpl_manager_data['manager_id'] = i
            fpl_players_all_managers_gws_data = pd.concat([fpl_players_all_managers_gws_data, fpl_manager_data], axis=0)
        for j in range(start_event,max_gw):
            manager_weekly_string = 'https://fantasy.premierleague.com/api/entry/' \
                                    + str(i) + '/event/' + str(j) + '/picks/'
            temp_r_weekly = requests.get(manager_weekly_string)
            temp_x_weekly = temp_r_weekly.json()
            fpl_manager_data = pd.DataFrame(temp_x_weekly['picks'])
            fpl_manager_data['gw'] = j
            fpl_manager_data['manager_id'] = i
            fpl_players_all_managers_gws_data = pd.concat([fpl_players_all_managers_gws_data,fpl_manager_data], axis=0)


# Mapping Chips and Wildcard information

manager_chips_string = 'https://fantasy.premierleague.com/api/entry/6484780/history/'
temp_ch_weekly = requests.get(manager_chips_string)
temp_ch_weekly = temp_ch_weekly.json()
manager_chips_data = pd.DataFrame(temp_ch_weekly['chips'])
manager_chips_data['manager_id'] = 6484780

all_managers_chips_data = manager_chips_data

for i in ids:
    manager_chips_string = 'https://fantasy.premierleague.com/api/entry/' + str(i) + '/history/'
    temp_ch_weekly = requests.get(manager_chips_string)
    temp_ch_weekly = temp_ch_weekly.json()
    temp_manager_chips_data = pd.DataFrame(temp_ch_weekly['chips'])
    temp_manager_chips_data['manager_id'] = i
    all_managers_chips_data = pd.concat([all_managers_chips_data, temp_manager_chips_data], axis=0)

# Mapping Transfers

manager_chips_data = pd.DataFrame(temp_ch_weekly['transfers'])


# FPL all players