'''
Package for the automatic computing of scores and rankings for the Play.it Dinasty keeper league
Andrea Pinna (andreapinna@gmail.com)
'''


import argparse
import os
import tools


def parse_arguments():

    '''
    Parse arguments
    '''

    # Initialize parser
    parser = argparse.ArgumentParser()

    # Parse arguments
    parser.add_argument('--games', dest='games', help='Select the range of games whose scores will be retrieved')
    parser.add_argument('--retrieve_scores', dest='retrieve_scores', default=False, action='store_true', help='Retrieve scores for the selected games')
    parser.add_argument('--print_rankings', dest='print_rankings', default=False, action='store_true', help='Print rankings updated to the last game retrieved')
    parser.add_argument('--run_dir', dest='run_dir', default=os.getcwd(), help='Select the directory containing the .py files')
    parser.add_argument('--data_dir', dest='data_dir', default=os.getcwd(), help='')
    parser.add_argument('--home_bonus_score', dest='home_bonus_score', type=int, default=5, help='')
    parser.add_argument('--n_best_scores', dest='n_best_scores', type=int, default=10, help='')
    parser.add_argument('--league_id', dest='league_id', type=int, default=170806, help='')


    return parser.parse_args()


def set_up_run(args):

    '''
    Create file and folder names
    '''

    args.data_file = os.path.join(args.run_dir, 'dinasty.yaml')
    args.schedule_file = os.path.join(args.run_dir, 'schedule_2016-17.yaml')
    args.league_url = 'http://basketball.sports.ws/game/%d' % args.league_id
    args.scores_dir = os.path.join(args.data_dir, 'scores')
    args.forum_games_dir = os.path.join(args.data_dir, 'forum-games')
    args.games_dir = os.path.join(args.data_dir, 'games')
    args.stats_dir = os.path.join(args.data_dir, 'stats')

    if args.retrieve_scores:
        r = args.games.split(',')
        if len(r) == 2:
            args.range = range(int(r[0]), int(r[1]) + 1)

    tools.make_directory(args.data_dir)
    tools.make_directory(args.scores_dir)
    tools.make_directory(args.stats_dir)
    tools.make_directory(args.forum_games_dir)
    tools.make_directory(args.games_dir)


    return args


def make_directory(dir_name):

    '''
    Create directory if it does not exist yet
    '''

    if not os.path.isdir(dir_name):
        os.mkdir(dir_name)
