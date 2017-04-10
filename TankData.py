'''


'''


TYPE_MAP = {'AT-SPG': 'TD',
            'mediumTank': 'MT',
            'heavyTank': 'HT',
            'lightTank': 'LT',
            'SPG': 'SPG'}

class TankData(object):
    '''
    
    wot (<class 'wargaming.WoT'>): 
    account_tank_ids (list): all tanks ids for the current account
    '''
    @property
    def wot(self):
        '''<class 'wargaming.WoT'>: '''
        return self._wot

    @property
    def tanks(self):
        ''''''
        return self._tanks

    def name(self, tank_id):
        '''
        '''
        return self.tanks[str(tank_id)]['name'].encode("utf-8")

    def type(self, tank_id):
        ''''''
        tank_type = self.tanks[str(tank_id)]['type']
        return TYPE_MAP[tank_type]

    def nation(self, tank_id):
        ''''''
        return self.tanks[str(tank_id)]['nation']

    def __init__(self, wot, account_tank_ids):
        self._wot = wot
        ati = [str(x) for x in account_tank_ids]
        tank_data = self.wot.encyclopedia.vehicles(fields='type, name, nation')
        self._tanks = {tank_id: tank_data[tank_id] for tank_id in tank_data.keys() if tank_id in ati}
        for tid in account_tank_ids:
            print '{0} {1} {2}'.format(self.name(tid), self.type(tid), self.nation(tid))
