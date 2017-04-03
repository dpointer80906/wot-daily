'''

'''
import pprint
import wargaming


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
        '''dict: tank_id: tank_name'''
        return self._vehicles

    def __init__(self, args):
        self._wot = wargaming.WoT(args.appid, region='na', language='en')
        player = self.wot.account.list(search=args.player)
        self._account_id = player[0]['account_id']
        account_vehicles = self.wot.account.tanks(account_id=self.account_id, fields="tank_id")
        account_tank_ids = [x['tank_id'] for x in account_vehicles[self.account_id]]
        vehicle_id2names = self.wot.encyclopedia.vehicles(fields='name')
        self._vehicles = {tank_id: vehicle_id2names[tank_id]['name'] for tank_id in vehicle_id2names.keys()}
        for tid in account_tank_ids:
            print self.vehicles[str(tid)]
