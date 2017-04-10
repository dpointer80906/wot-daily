'''

'''
import wargaming
import TankData


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

    def __init__(self, args):
        self._wot = wargaming.WoT(args.appid, region='na', language='en')
        player = self.wot.account.list(search=args.player)
        self._account_id = player[0]['account_id']
        account_vehicles = self.wot.account.tanks(account_id=self.account_id, fields="tank_id")
        account_tank_ids = [x['tank_id'] for x in account_vehicles[self.account_id]]
        TankData.TankData(self.wot, account_tank_ids)
