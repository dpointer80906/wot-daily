'''Module for main() invocation and command line parsing.
'''
import sys
import argparse
import logging
import DailyStats


SUCCESS = 0
FAILURE = 1
APPID = 'demo'


def parseargs():
    '''Command line argument parser.
    
    Returns:
        (Namespace): the parsed command line args.
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'player',
        help='player name')
    parser.add_argument(
        '--appid',
        default=APPID,
        help='Wargaming.net application id (default: %(default)s)')
    args = parser.parse_args()
    return args


def main():
    '''Parse command line args & execute.
    
    Returns:
        int: SUCCESS | FAILURE.
    '''
    logging.basicConfig(stream=sys.stdout, format='%(asctime)s %(message)s', level=logging.INFO)
    args = parseargs()
    ds = DailyStats.DailyStats(args)
    return SUCCESS


if __name__ == '__main__':
    main()
