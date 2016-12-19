'''
Package for the automatic computing of scores and rankings for the Play.it Dinasty keeper league
Andrea Pinna (andreapinna@gmail.com)
'''


from bs4 import BeautifulSoup
import urllib2
import logging
import yaml
import os
import tools


logging.basicConfig(format='%(message)s', level=logging.DEBUG)


def load_teams(data_file):

    '''
    Load the data structure containing information about teams
    '''

    teams = yaml.load(open(data_file))
    logging.info('Data structure with team information loaded!')
    return teams


def load_schedule(schedule_file):

    '''
    Load the league schedule
    '''

    schedule = yaml.load(open(schedule_file))
    logging.info('Schedule loaded!')
    return schedule


def get_team_by_id(data_file, team_id, teams=None):

    '''
    Load information about a team according to its own identifier
    '''

    if not teams:
        teams = load_teams(data_file)

    team = [t for t in teams if t['hn'] == team_id][0]
    return team


def get_team_by_city(data_file, team_city, teams=None):

    '''
    Load information about a team according to its own city name
    '''

    if not teams:
        teams = load_teams(data_file)

    team = [t for t in teams if t['city'] == team_city][0]
    return team


def load_game(args, game_id, away_team_id, home_team_id, teams=None):

    '''
    Retrieve the boxscore for the selected game
    '''

    if not teams:
        teams = load_teams(args.data_file)

    away_team = get_team_by_id(args.data_file, away_team_id, teams)
    home_team = get_team_by_id(args.data_file, home_team_id, teams)
    logging.debug('Loading game %d: %s @ %s...', game_id, away_team['city'], home_team['city'])
    game_url = '%s/%d/%d/%d' % (args.league_url, game_id, away_team_id, home_team_id)
    game_url = game_url + '?league=170806'
    logging.info(game_url)
    response = urllib2.urlopen(game_url)
    html = response.read()
    soup = BeautifulSoup(html)
    return soup


def get_team_score(args, table, home):

    '''
    Compute the final score for a team given its boxscore
    '''

    # Get rows from boxscore
    rows = table.findAll('tr')
    team_fps = []
    file_rows = []

    # Iterate on players (even rows)
    for tr in rows[2:26:2]:
        # Columns for the given row
        cols = tr.findAll('td')
        # Link to the player webpage
        # player_id = str(cols[0].findAll('a')[0]['href'])
        # Player name
        player = str(cols[0].find(text=True))
        # Get fantasy points
        try:
            # FP value, plus any technical foul (which are removed by basketball.sports.ws)
            #fps = int(cols[5].find(text=True)) + int(cols[13].find(text=True))
            fps = int(cols[5].find(text=True))
        except:
            # Player get a DNP if a score is not specified
            fps = 'DNP'
        # Print and append player name and his FPs
        row_string = '%s\t%s' % (player, fps)
        logging.debug(row_string)
        file_rows.append(row_string)
        team_fps.append(fps)

    # Sort points from highest to lowest
    team_fps.sort(reverse=True)
    # Select all numerical points
    num_points = [num for num in team_fps if isinstance(num, (int, float))]
    # Compute score from "n" best performances
    if len(num_points) <= args.n_best_scores:
        score = sum(num_points)
    else:
        score = sum(num_points[0:args.n_best_scores])

    # Add bonus points to home team
    if home == 'home':
        score += args.home_bonus_score
        file_rows.append('HOME/AWAY\t%d' % args.home_bonus_score)
    else:
        file_rows.append('HOME/AWAY\t0')

    # Print final score
    final_score_string = 'FINAL SCORE\t%d' % score
    file_rows.append(final_score_string)

    return score, file_rows


def get_game_score(args, game_id, away_team_id, home_team_id, teams=None, save=False):

    '''
    Compute the final score of a game
    '''

    if not teams:
        teams = load_teams(args.data_file)

    # Load game data from Hoops
    soup = load_game(args, game_id, away_team_id, home_team_id, teams=teams)

    # Get score for the away team
    away_table = soup('table')[0]
    away_team = get_team_by_id(args.data_file, away_team_id, teams=teams)
    logging.debug('Computing scores for team %s', away_team['city'])
    away_score, away_rows = get_team_score(args, away_table, 'away')

    # Get score for the home team
    home_table = soup('table')[1]
    home_team = get_team_by_id(args.data_file, home_team_id, teams=teams)
    logging.debug('Computing scores for team %s', home_team['city'])
    home_score, home_rows = get_team_score(args, home_table, 'home')

    # Print final score for this game
    log_string = '%s @ %s %d-%d' % (away_team['city'], home_team['city'], away_score, home_score)
    logging.info(log_string)

    # Assign W and L to teams
    if home_score > away_score:
        game_string = '%s @ [b]%s[/b] %d-[b]%d[/b]' % (away_team['city'], home_team['city'], away_score, home_score)
    elif home_score < away_score:
        game_string = '[b]%s[/b] @ %s [b]%d[/b]-%d' % (away_team['city'], home_team['city'], away_score, home_score)
    else:
        game_string = '%s @ %s %d-%d WARNING!!! A TIE!!! WARNING!!!' % (away_team['city'], home_team['city'], away_score, home_score)

    # Save scores to file
    if save:
        save_team_score(args, game_id, away_team, away_rows)
        save_team_score(args, game_id, home_team, home_rows)

    return game_string, log_string


def save_team_score(args, game_id, team, rows):

    '''
    Save to file the score of a game by a team
    '''

    # Create team directory if it does not exist yet
    team_directory = os.path.join(args.scores_dir, team['city'])
    tools.make_directory(team_directory)
    # File to save the team score
    file_name = 'GAME-%d.txt' % game_id
    file_path = os.path.join(team_directory, file_name)

    # Save the score for the current team
    with open(file_path, 'w') as f:
        f.write('%s %s\tGAME %d\n' % (team['city'], team['nick'], game_id))
        for line in rows:
            f.write('%s\n' % line)


def save_game_scores(args, game_id, game_rows, log_rows):

    '''
    Save to file the scores of a game
    '''

    # File to save the game scores
    file_name = 'GAME-%d_SCORES.txt' % game_id
    # Save the scores of the current game (in forum friendly format)
    file_path = os.path.join(args.forum_games_dir, file_name)
    with open(file_path, 'w') as f:
        f.write('[b]Game %d[/b]\n' % game_id)
        for line in game_rows:
            f.write('%s\n' % line)

    # Save the scores of the current game
    file_path = os.path.join(args.games_dir, file_name)
    with open(file_path, 'w') as f:
        f.write('Game %d\n' % game_id)
        for line in log_rows:
            f.write('%s\n' % line)


def get_all_game_scores(args, game_id, teams=None, schedule=None, save=False):

    '''
    Retrieve the scores for all the matches of a particular game
    '''
    # Load teams
    if not teams:
        teams = load_teams(args.data_file)

    # Load schedule
    if not schedule:
        schedule = load_schedule(args.schedule_file)

    # Select desired game
    desired_game = 'Game %d' % game_id
    logging.info('\n')
    logging.info(desired_game)
    game_list = schedule[desired_game]
    game_rows = []
    log_rows = []
    # Iterate on matches of the selected game
    for game in game_list:
        # Get teams for the current match
        away_team = get_team_by_city(args.data_file, game.split(' @ ')[0], teams=teams)
        home_team = get_team_by_city(args.data_file, game.split(' @ ')[1], teams=teams)
        # Get scores for the current match
        game_string, log_string = get_game_score(args, game_id, away_team['hn'], home_team['hn'], teams=teams, save=save)
        game_rows.append(game_string)
        log_rows.append(log_string)

    # Save scores of the selected game
    if save:
        save_game_scores(args, game_id, game_rows, log_rows)

