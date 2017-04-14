'''

'''
import wargaming
import Vehicles


class DailyStats(object):
    '''

    '''
    @property
    def wot(self):
        '''<class 'wargaming.WoT'>: '''
        return self._wot

    @property
    def account_id(self):
        '''int: '''
        return self._account_id

    @property
    def vehicles(self):
        '''<Vehicles>: '''
        return self._vehicles

    def __init__(self, args):
        self._wot = wargaming.WoT(args.appid, region='na', language='en')
        player = self.wot.account.list(search=args.player)
        self._account_id = player[0]['account_id']
        self._vehicles = Vehicles.Vehicles(self.wot, self.account_id)
        self.vehicles.add_vehicle_stats(6913)

