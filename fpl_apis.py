import pandas as pd
import numpy as np
import json
import requests

# Bootstrap API
r_boot = requests.get('https://fantasy.premierleague.com/api/bootstrap-static/')
x_boot = r_boot.json()

boot_keys = list(x_boot.keys())
boot_keys.pop('game_settings')

for i in boot_keys:
    i = pd.DataFrame(x_boot[i])

# Fixtures API
r_fixtures = requests.get('https://fantasy.premierleague.com/api/fixtures/')
x_fixtures = r_fixtures.json()

# GW Specific Fixtures API [GW-1]
r_gw_fixtures = requests.get('https://fantasy.premierleague.com/api/fixtures/?event=1')
x_gw_fixtures = r_boot.json()

# Live results of given GW, it should be numeric
r_gw_live = requests.get('https://fantasy.premierleague.com/api/event/1/live/')
x_gw_live = r_gw_live.json()

# General info about team Manager ID, such as name, manager, kit colors, leagues joined
r_manager_info = requests.get('https://fantasy.premierleague.com/api/entry/58575/')
x_manager_info = r_manager_info.json()

# This season and previous season performance of given manager
r_manager_history = requests.get('https://fantasy.premierleague.com/api/entry/58575/history/')
x_manager_history = r_manager_history.json()

# All transfers of given manager
r_manager_transfers = requests.get('https://fantasy.premierleague.com/api/entry/58575/transfers/')
x_manager_transfers = r_manager_transfers.json()

# Squad picks of manager for particular GW. [M:57, GW:1]
r_manager_gw_picks = requests.get('https://fantasy.premierleague.com/api/entry/58575/event/1/picks/')
x_manager_gw_picks = r_manager_gw_picks.json()

# Information about league with id LID, such as name and standings
r_league_info = requests.get('https://fantasy.premierleague.com/api/leagues-classic/667096/standings/')
x_league_info = r_league_info.json()

# Page for leagues LID with more than 50 teams
r_league_page_info = requests.get('https://fantasy.premierleague.com/api/leagues-classic/667096/standings/?page_standings=3')
x_league_page_info = r_league_page_info.json()

# Actual Football players performance summary
r_player_info = requests.get('https://fantasy.premierleague.com/api/element-summary/1/')
x_player_info = r_player_info.json()

# FPL Regions
r_regions = requests.get('https://fantasy.premierleague.com/api/regions/')
x_regions = r_regions.json()

# List of Best Leagues
r_best_leagues = requests.get('https://fantasy.premierleague.com/api/stats/best-classic-private-leagues/')
x_best_leagues= r_best_leagues.json()




