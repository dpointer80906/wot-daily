'''
'''
import wargaming
import Vehicles


class DailyStats(object):
    '''
    '''
    @property
    def wot(self):
        '''<class 'wargaming.WoT'>: base class for operations on wargaming.net API.'''
        return self._wot

    @property
    def account_id(self):
        '''int: account id for named player in args.'''
        return self._account_id

    @property
    def vehicles(self):
        '''<Vehicles>: class for wot database interaction.'''
        return self._vehicles

    def __init__(self, args):
        self._wot = wargaming.WoT(args.appid, region='na', language='en')
        player = self.wot.account.list(search=args.player)
        self._account_id = player[0]['account_id']
        self._vehicles = Vehicles.Vehicles(self.wot, self.account_id)
        self.vehicles.current_vehicle_stats(6913)
