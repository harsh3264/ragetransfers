import pandas as pd
import numpy as np
import json
import requests
# from __future__ import print_function
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from fpl_pre_process import fpl_players_collab
import pickle

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


fpl_league_report = all_leagues_data.rename({'entry': 'manager_id',
                                             'player_name': 'manager_name',
                                             'entry_name': 'team_name',
                                             'total': 'points'}, axis=1)

fpl_league_report = fpl_league_report[['manager_id', 'manager_name', 'team_name', 'points']]


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
        for j in range(start_event,max_gw+1):
            manager_weekly_string = 'https://fantasy.premierleague.com/api/entry/' \
                                    + str(i) + '/event/' + str(j) + '/picks/'
            temp_r_weekly = requests.get(manager_weekly_string)
            temp_x_weekly = temp_r_weekly.json()
            fpl_manager_data = pd.DataFrame(temp_x_weekly['picks'])
            fpl_manager_data['gw'] = j
            fpl_manager_data['manager_id'] = i
            fpl_players_all_managers_gws_data = pd.concat([fpl_players_all_managers_gws_data,fpl_manager_data], axis=0)


# Mapping Chips and current progress information

manager_chips_string = 'https://fantasy.premierleague.com/api/entry/6484780/history/'
temp_ch_weekly = requests.get(manager_chips_string)
temp_ch_weekly = temp_ch_weekly.json()
manager_chips_data = pd.DataFrame(temp_ch_weekly['chips'])
manager_chips_data['manager_id'] = 6484780

manager_current_season_data = pd.DataFrame(temp_ch_weekly['current'])
manager_current_season_data['manager_id'] = 6484780

all_managers_chips_data = manager_chips_data

all_managers_current_season_data = manager_current_season_data

for i in ids:
    manager_chips_string = 'https://fantasy.premierleague.com/api/entry/' + str(i) + '/history/'
    temp_ch_weekly = requests.get(manager_chips_string)
    temp_ch_weekly = temp_ch_weekly.json()
    temp_manager_chips_data = pd.DataFrame(temp_ch_weekly['chips'])
    temp_manager_chips_data['manager_id'] = i
    all_managers_chips_data = pd.concat([all_managers_chips_data, temp_manager_chips_data], axis=0)
    temp_manager_current_season_data = pd.DataFrame(temp_ch_weekly['current'])
    temp_manager_current_season_data['manager_id'] = i
    all_managers_current_season_data = pd.concat([all_managers_current_season_data, temp_manager_current_season_data], axis=0)

# Mapping Transfers

manager_transfers_string = 'https://fantasy.premierleague.com/api/entry/6484780/transfers/'
temp_tr_weekly = requests.get(manager_transfers_string)
temp_tr_weekly = temp_tr_weekly.json()
manager_transfers_data = pd.DataFrame(temp_tr_weekly)
manager_transfers_data['manager_id'] = 6484780

all_managers_transfers_data = manager_transfers_data

for i in ids:
    manager_transfers_string = 'https://fantasy.premierleague.com/api/entry/' + str(i) + '/transfers/'
    temp_tr_weekly = requests.get(manager_transfers_string)
    temp_tr_weekly = temp_tr_weekly.json()
    temp_manager_transfers_data = pd.DataFrame(temp_tr_weekly)
    temp_manager_transfers_data['manager_id'] = i
    all_managers_transfers_data = pd.concat([all_managers_transfers_data, temp_manager_transfers_data], axis=0)



# FPL managers GW performances

fpl_managers_gw_performances = fpl_players_all_managers_gws_data.rename({'position': 'pick_order', 'multiplier': 'captain_points'}, axis=1)\
    .merge(fpl_players_collab,
           left_on=['element', 'gw'], right_on=['player_id','round'], how='left')

# fpl_managers_gw_performances = fpl_managers_gw_performances[[
#     'player_id', 'manager_id', 'gw', 'pick_order',
#     'captain_points', 'player_name', 'position', 'team_name']]

fpl_managers_gw_performances = fpl_managers_gw_performances.merge(fpl_league_report.rename({'team_name': 'manager_team_name'}, axis=1), on='manager_id')

fpl_managers_gw_performances['added_cap_points'] = fpl_managers_gw_performances['captain_points'] * fpl_managers_gw_performances['round_points']


fpl_managers_gw_performances = fpl_managers_gw_performances[[
    'player_id', 'manager_id', 'gw', 'pick_order',
    'captain_points', 'player_name', 'position', 'team_name',
    'round_points', 'added_cap_points', 'goals_scored', 'assists',
    'clean_sheets', 'own_goals', 'penalties_saved', 'penalties_missed',
    'yellow_cards', 'red_cards', 'saves', 'bonus', 'manager_team_name',
    'manager_name', 'opponent_name']]

fpl_managers_gw_performances.to_csv('FPL_GW_LEVEL_DATA.csv', header=True, index=False)
#
# fpl_managers_gw_performances = pd.read_csv("/Users/Harsh/Desktop/ragetransfers/FPL_GW_LEVLE_DATA.csv")


''' Adding Chips info for all managers'''

fpl_managers_gw_performances_bb = fpl_managers_gw_performances.merge(all_managers_chips_data.rename({'manager_id':'m_id', 'name':'chips'}, axis=1),
                                                                     left_on=['manager_id', 'gw'],
                                                                     right_on=['m_id', 'event'], how='left')

fpl_managers_gw_performances_bb = fpl_managers_gw_performances_bb.fillna(0)

cols_need = fpl_managers_gw_performances.columns.to_list() + ['chips']

fpl_managers_gw_performances_bb = fpl_managers_gw_performances_bb[cols_need]

def label_def (row):
   if row['position'] == 'DEF':
      return 1
   return 0

def label_mid (row):
   if row['position'] == 'MID':
      return 1
   return 0

def label_fwd (row):
   if row['position'] == 'FWD':
      return 1
   return 0

def label_cs (row):
   if row['position'] == 'DEF' or row['position'] == 'GKP':
      return row['clean_sheets']
   return 0

def label_cap (row):
   if row['captain_points'] >= 2:
      return row['added_cap_points']
   return 0

fpl_managers_gw_performances_bb['def'] = fpl_managers_gw_performances_bb.apply (lambda row: label_def(row), axis=1)

fpl_managers_gw_performances_bb['mid'] = fpl_managers_gw_performances_bb.apply (lambda row: label_mid(row), axis=1)

fpl_managers_gw_performances_bb['fwd'] = fpl_managers_gw_performances_bb.apply (lambda row: label_fwd(row), axis=1)

fpl_managers_gw_performances_bb['GW_captain_points'] = fpl_managers_gw_performances_bb.apply (lambda row: label_cap(row), axis=1)

fpl_managers_gw_performances_bb['GW_clean_sheets'] = fpl_managers_gw_performances_bb.apply (lambda row: label_cs(row), axis=1)


temp_df_1 = fpl_managers_gw_performances_bb[fpl_managers_gw_performances_bb['chips'] != 'bboost'].reset_index(drop=True)

sub_temp_df = temp_df_1[temp_df_1['pick_order'] <= 11].reset_index(drop=True)

temp_df_2 = fpl_managers_gw_performances_bb[fpl_managers_gw_performances_bb['chips'] == 'bboost'].reset_index(drop=True)

main_temp_df = pd.concat([sub_temp_df, temp_df_2], axis=0).reset_index(drop=True)

grp_list = ['manager_id','manager_team_name','manager_name','gw']

agg_list = ['added_cap_points', 'GW_captain_points', 'goals_scored', 'assists',
            'GW_clean_sheets', 'bonus', 'saves', 'yellow_cards', 'red_cards',
            'penalties_saved', 'penalties_missed', 'def', 'mid', 'fwd']


master_gw_file = main_temp_df.groupby(grp_list, as_index=False)[agg_list].sum()

gw_cap_name = fpl_managers_gw_performances[fpl_managers_gw_performances.captain_points >= 2].reset_index(drop=True)

gw_cap_name = gw_cap_name[['manager_id', 'gw', 'player_name']]

all_managers_current_season_data['bank_value'] = all_managers_current_season_data['bank']/10

all_managers_current_season_data['team_value'] = all_managers_current_season_data['value']/10

fpl_gw_level_analysis_p1 = master_gw_file.merge(gw_cap_name.rename({'player_name':'captain_name'}, axis=1), on=['manager_id', 'gw'], how='left')

fpl_gw_level_analysis_p2 = fpl_gw_level_analysis_p1.merge(all_managers_chips_data.rename({'event':'gw', 'name':'chips'}, axis=1), on=['manager_id', 'gw'], how='left')

fpl_gw_level_analysis_p3 = fpl_gw_level_analysis_p2.merge(all_managers_current_season_data.rename({'event':'gw', 'event_transfers':'gw_transfers', 'rank':'gw_rank'}, axis=1), on=['manager_id', 'gw'], how='left')

fpl_gw_level_analysis_p3['gw_hits'] = 0 - fpl_gw_level_analysis_p3['event_transfers_cost']

final_cols = fpl_gw_level_analysis_p1.columns.to_list() + \
             ['chips', 'gw_transfers', 'gw_hits', 'points_on_bench',
              'team_value', 'bank_value', 'gw_rank', 'overall_rank']

fpl_gw_level_analysis = fpl_gw_level_analysis_p3[final_cols]

fpl_gw_level_analysis['formation'] = fpl_gw_level_analysis['def'].astype(str) + '-' + fpl_gw_level_analysis['mid'].astype(str) + '-' + fpl_gw_level_analysis['fwd'].astype(str)

fpl_gw_level_analysis = fpl_gw_level_analysis.rename({'added_cap_points':'points', 'GW_clean_sheets':'clean_sheets', 'GW_captain_points': 'Captain_Points'}, axis=1)

fpl_gw_level_analysis = fpl_gw_level_analysis.fillna(0)


def label_wildcard (row):
   if row['name'] == 'wildcard':
      return 1
   return 0

def label_3xc (row):
    if row['name'] == '3xc':
        return 1
    return 0

def label_bboost (row):
    if row['name'] == 'bboost':
        return 1
    return 0

def label_freehit (row):
    if row['name'] == 'freehit':
        return 1
    return 0

all_managers_chips_data['wildcard'] = all_managers_chips_data.apply (lambda row: label_wildcard(row), axis=1)

all_managers_chips_data['3xc'] = all_managers_chips_data.apply (lambda row: label_3xc(row), axis=1)

all_managers_chips_data['bboost'] = all_managers_chips_data.apply (lambda row: label_bboost(row), axis=1)

all_managers_chips_data['freehit'] = all_managers_chips_data.apply (lambda row: label_freehit(row), axis=1)

total_grp = ['manager_id', 'manager_team_name', 'manager_name']

total_agg = ['points', 'Captain_Points', 'goals_scored', 'assists', 'clean_sheets',
             'bonus', 'saves', 'yellow_cards', 'red_cards', 'penalties_saved', 'penalties_missed',
             'gw_transfers', 'gw_hits', 'points_on_bench']

fpl_total_analysis_p1 = fpl_gw_level_analysis.groupby(total_grp, as_index=False)[total_agg].sum()

current_season_max = all_managers_current_season_data[all_managers_current_season_data['event'] == max_gw].reset_index(drop=True)

current_season_max = current_season_max[['bank_value', 'team_value', 'manager_id', 'event', 'overall_rank']]

fpl_total_analysis_p2 = fpl_total_analysis_p1.merge(current_season_max.rename({'event':'gw', 'event_transfers':'gw_transfers', 'rank':'gw_rank'}, axis=1), on=['manager_id'], how='left')

current_season_chips = all_managers_chips_data.groupby('manager_id', as_index=False)['wildcard', 'bboost', '3xc', 'freehit'].sum()

fpl_total_analysis_p3 = fpl_total_analysis_p2.merge(current_season_chips, on=['manager_id'], how='left')

fpl_total_analysis_p3 = fpl_total_analysis_p3.fillna(0)

fpl_total_analysis_p3['Total_Points'] = fpl_total_analysis_p3['points'] + fpl_total_analysis_p3['gw_hits']

fpl_total_analysis = fpl_total_analysis_p3.sort_values(['Total_Points', 'gw_hits', 'overall_rank'], ascending=[False, False, True])

fpl_total_analysis = fpl_total_analysis.rename({'gw_hits':'total_hits', 'gw_transfers':'total_transfers', 'points':'Points_without_hits'}, axis=1)


SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# here enter the id of your google sheet
WIZARDS_FPL = '1rfof1k-B_MJ2onYCHFdyYo0PxTUyGvWADtlsa7lQJwA'
RAW_DATA = 'RAW_DATA!A1'

def main():
    global values_input, service
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '/Users/Harsh/Desktop/ragetransfers/src/rg_cred_2.json', SCOPES) # here enter the name of your downloaded JSON file
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result_input = sheet.values().get(spreadsheetId=WIZARDS_FPL,
                                range=RAW_DATA).execute()
    values_input = result_input.get('values', [])

    if not values_input and not values_expansion:
        print('No data found.')

main()

def Export_DATA(sheet, range, df):
    response_date = service.spreadsheets().values().update(
        spreadsheetId=sheet,
        valueInputOption='RAW',
        range=range,
        body=dict(
            majorDimension='ROWS',
            values=df.T.reset_index().T.values.tolist())
    ).execute()
    print('Data successfully Updated in ' + str(range))

Export_DATA(WIZARDS_FPL, RAW_DATA, fpl_managers_gw_performances_bb)

j = 1

for i in range(1, max_gw+1):
    temp_gw_a = fpl_gw_level_analysis[fpl_gw_level_analysis['gw'] == i].reset_index(drop=True)
    temp_gw_a = temp_gw_a.sort_values(['points', 'gw_hits', 'overall_rank'], ascending=[False, False, True])
    GW_LEVEL_DATA = 'GW_Level_P!A' + str(j)
    Export_DATA(WIZARDS_FPL, GW_LEVEL_DATA, temp_gw_a)
    j = j + (len(temp_gw_a)) + 3


OVERALL_DATA = 'OVERALL_P!A1'

Export_DATA(WIZARDS_FPL, OVERALL_DATA, fpl_total_analysis)







# df= pd.DataFrame(values_input[1:], columns=values_input[0])




