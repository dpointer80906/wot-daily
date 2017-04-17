'''Command line module for main() invocation and command line argument parsing.
'''
import sys
import argparse
import logging
import DailyStats
from constants import DEFAULT_APPID


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
        default=DEFAULT_APPID,
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
    return ds.vehicles.status


if __name__ == '__main__':
    main()
