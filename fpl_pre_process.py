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