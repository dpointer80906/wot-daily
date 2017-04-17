'''Constants for the wot-daily project.
'''

SUCCESS = 0
FAILURE = 1
DEFAULT_APPID = 'demo'
DEFAULT_DB = 'sqlite:///wot.sqlite'

'''str: field data to obtain from wargaming.net for each account vehicle.'''
VEHICLE_FIELDS = 'type, name, nation, tier'

'''dict: wargaming.net type names to local type names.'''
TYPE_MAP = {'AT-SPG': 'TD',
            'mediumTank': 'MT',
            'heavyTank': 'HT',
            'lightTank': 'LT',
            'SPG': 'SPG'}

'''dict: wargaming.net nation names to local nation names.'''
NATION_MAP = {'ussr': 'USSR',
              'usa': 'USA',
              'france': 'FR',
              'germany': 'GE',
              'uk': 'UK',
              'china': 'CH',
              'japan': 'JP'}
