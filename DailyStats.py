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

    def __init__(self, args):
        self._wot = wargaming.WoT(args.appid, region='na', language='en')
        player = self.wot.account.list(search=args.player)
        self._account_id = player[0]['account_id']
        result = self.wot.account.tanks(account_id=self.account_id)
        pprint.pprint(result[self.account_id])
