'''
Package for the automatic computing of scores and rankings for the Play.it Dinasty keeper league
Andrea Pinna (andreapinna@gmail.com)
'''


import scores
import stats
import sys
import tools


def main():

    '''
    Run the software to retrieve the data, compute some statistics
    and output the league rankings.
    '''

    # Parse arguments from command line
    args = tools.parse_arguments()

    # Create names for folders and files
    args = tools.set_up_run(args)

    # Retrieve scores and compute stats
    if args.retrieve_scores:
        # Iterate on the games in range
        for i in args.range:
            # Retrieve the scores from basketball.sports.ws
            scores.get_all_game_scores(args, i, save=True)
            # Compute statistics from the saved files
            stats.get_scores_from_file(args, i)

    # Print league rankings to screen
    if args.print_rankings:
        stats.print_league_rankings(args)


if __name__ == "__main__":

    '''
    Nothing to see here :forza:
    '''

    sys.exit(main())
