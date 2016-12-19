'''
Package for the automatic computing of scores and rankings for the Play.it Dinasty keeper league
Andrea Pinna (andreapinna@gmail.com)
'''


import numpy
import os
import scores


def print_league_rankings(args, teams=None):

    '''
    Print the division and conference rankings of the league
    '''

    # Load teams
    if not teams:
        teams = scores.load_teams(args.data_file)

    # Initialize dictionary
    td = dict()

    # Iterate on teams
    for t in teams:
        city = t['city']
        # Load team data
        team_data = read_team_stats(args, city)
        # Load team statistics
        team_stats = compute_team_stats(team_data)
        # Print stats for the current team
        td.update({city: team_stats})
        team_string = '%s\t%s' % (city, str("{:3.2f}".format(td[city]['ppg'])))
        print team_string

    # List teams by number of wins and then by points per game
    teams_by_wins_and_ppg = sorted(td, key=lambda team: (-td[team]['ws'], -td[team]['ppg']))

    # Print divisional rankings
    for div in ['atl', 'ctl', 'mdw', 'pac']:
        divisional_rankings(args, td, teams, teams_by_wins_and_ppg, div)

    # Print conference rankings
    for conf in ['est', 'wst']:
        conference_rankings(args, td, teams, teams_by_wins_and_ppg, conf)

    return td


def divisional_rankings(args, td, teams, twp, div):

    '''
    Print the rankings for the selected division
    '''

    # Select the teams of the current division
    div_tms = [t for t in twp if scores.get_team_by_city(args, t, teams=teams)['dv'] == div]
    if div == 'atl':
        print '\n%s  W-L  PPGM   PPGA' % 'Atlantic Division'.ljust(25)
    elif div == 'ctl':
        print '\n%s  W-L  PPGM   PPGA' % 'Central Division'.ljust(25)
    elif div == 'mdw':
        print '\n%s  W-L  PPGM   PPGA' % 'Midwest Division'.ljust(25)
    elif div == 'pac':
        print '\n%s  W-L  PPGM   PPGA' % 'Pacific Division'.ljust(25)
    else:
        print 'ERROR!!!'

    # Print divisional rankings
    for t in div_tms:
        print (t + ' ' + scores.get_team_by_city(args, t, teams=teams)['nick']).ljust(25), td[t]['record'],\
        str("{:3.2f}".format(td[t]['ppg'])), str("{:3.2f}".format(td[t]['allowed-ppg']))


def conference_rankings(args, td, teams, twp, conf):

    '''
    Print the rankings for the selected conference
    '''

    # Select the teams of the current conference
    conf_tms = [t for t in twp if scores.get_team_by_city(args, t, teams=teams)['cf'] == conf]
    if conf == 'est':
        print '\n%s  W-L  PPGM   PPGA' % 'Eastern Conference'.ljust(25)
    elif conf == 'wst':
        print '\n%s  W-L  PPGM   PPGA' % 'Western Conference'.ljust(25)

    # Print conference rankings
    for t in conf_tms:
        print (t + ' ' + scores.get_team_by_city(args, t, teams=teams)['nick']).ljust(25), td[t]['record'],\
        str("{:3.2f}".format(td[t]['ppg'])), str("{:3.2f}".format(td[t]['allowed-ppg']))


def compute_team_stats(data):

    '''
    Compute stats for the selected team
    '''

    # Initialize stats dictionary
    t = dict()
    # Point per game (made and allowed)
    t['ppg'] = numpy.mean(data['points-made'])
    t['allowed-ppg'] = numpy.mean(data['points-allowed'])
    # W-L count, winning percentage, W-L record
    t['ws'] = data['win-lost'].count('W')
    t['ls'] = data['win-lost'].count('L')
    t['pct'] = float(t['ws']) / len(data['win-lost'])
    t['record'] = str(t['ws']) + '-' + str(t['ls'])

    return t



def read_team_stats(args, team):

    '''
    Read stats for the selected team
    '''

    # Load stats for the selected team
    file_name = '%s-STATS.txt' % team
    file_path = os.path.join(args.stats_dir, file_name)
    t = initialize_stats_dict()
    with open(file_path, 'r') as f:
        # Iterate on played games
        for line in f:
            l = line.strip('\n').split('\t')
            t['games'].append(int(l[0].split(' ')[1]))
            t['home-away'].append(l[1])
            t['opponents'].append(l[2])
            t['win-lost'].append(l[3])
            t['cf-w-l'].append(l[4])
            t['ext-cf-w-l'].append(l[5])
            t['dv-w-l'].append(l[6])
            t['ext-dv-w-l'].append(l[7])
            t['points-made'].append(int(l[8]))
            t['points-allowed'].append(int(l[9]))

    return t


def initialize_stats_dict():

    '''
    Initialize the dictionary containing the stats for a team
    '''

    return {'games': [], 'home-away': [], 'opponents': [], 'win-lost': [], 'cf-w-l': [], 'ext-cf-w-l': [],
            'dv-w-l': [], 'ext-dv-w-l': [], 'points-made': [], 'points-allowed': []}



def print_conference_rankings():

    '''
    Print the most recently updated rankings for both conferences
    '''

    pass


def print_division_rankings():

    '''
    Print the most recently updated rankings for all divisions
    '''

    pass


def get_scores_from_file(args, game_id, teams=None):

    '''
    Read and print the scores for the selected game
    '''
    if not teams:
        teams = scores.load_teams(args.data_file)

    # Load scores of the current game
    file_name = 'GAME-%d_SCORES.txt' % game_id
    file_path = os.path.join(args.games_dir, file_name)
    with open(file_path, 'r') as f:
        for line in f:
            # Skip the line if it does not contain a score
            if line.startswith('Game'):
                pass
            else:
                # Get team names and scores
                line = line.strip('\n')
                away_team_name = line.split(' @ ')[0]
                home_team_name = line.split(' @ ')[1].strip('0123456789- ')
                print away_team_name
                print home_team_name
                # Load team data
                away_team = scores.get_team_by_city(args, away_team_name, teams=teams)
                home_team = scores.get_team_by_city(args, home_team_name, teams=teams)

                # Scores
                away_score = int(line.split(' ')[-1].split('-')[0])
                home_score = int(line.split(' ')[-1].split('-')[1])

                # Win or lost
                if away_score > home_score:
                    away_result = 'W'
                    home_result = 'L'

                else:
                    away_result = 'L'
                    home_result = 'W'

                # Conference wins
                if away_team['cf'] == home_team['cf']:
                    away_cf_result = away_result
                    home_cf_result = home_result
                    away_extra_cf_result = 'N'
                    home_extra_cf_result = 'N'
                else:
                    away_cf_result = 'N'
                    home_cf_result = 'N'
                    away_extra_cf_result = away_result
                    home_extra_cf_result = home_result

                # Division wins
                if away_team['dv'] == home_team['dv']:
                    away_dv_result = away_result
                    home_dv_result = home_result
                    away_extra_dv_result = 'N'
                    home_extra_dv_result = 'N'
                else:
                    away_dv_result = 'N'
                    home_dv_result = 'N'
                    away_extra_dv_result = away_result
                    home_extra_dv_result = home_result

                # Opponent
                away_opponent = home_team_name
                home_opponent = away_team_name
                #init_stat_file(args, home_team_name)
                #init_stat_file(args, away_team_name)
                # Update line for away team
                update_game_line(args, away_team_name, game_id, 'at', away_opponent, away_result, away_cf_result,
                                 away_extra_cf_result, away_dv_result, away_extra_dv_result, away_score, home_score)

                # Update line for home team
                update_game_line(args, home_team_name, game_id, 'vs', home_opponent, home_result, home_cf_result,
                                 home_extra_cf_result, home_dv_result, home_extra_dv_result, home_score, away_score)


def init_stat_file(args,team_name):
    file_name = '%s-STATS.txt' % team_name
    file_path = os.path.join(args.stats_dir, file_name)
    file_path.seek(0)
    file_path.truncate()
    

def update_game_line(args, team_name, game_id, home_away, opponent_team, result, cf_result, extra_cf_result, dv_result, extra_dv_result, score, opponent_score):
    '''
    Update the stats summary for the selected team
    '''
    # Select the file to be updated
    file_name = '%s-STATS.txt' % team_name
    file_path = os.path.join(args.stats_dir, file_name)
    # Append string with stats to the file
    with open(file_path, 'a') as f:
        s = 'Game %d\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%d\t%d\n' % (game_id, home_away, opponent_team, result, cf_result, extra_cf_result, dv_result, extra_dv_result, score, opponent_score)
        f.write(s)

