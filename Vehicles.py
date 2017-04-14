'''Module to collect relevant data from wargaming.net, merge into database & provide database services.
'''
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from datetime import datetime
import time

DB = 'sqlite:///wot.sqlite'

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

Base = declarative_base()


class VehiclesRow(Base):
    '''Represents a vehicles database table row.
    
    See https://developers.wargaming.net/reference/all/wot/encyclopedia/vehicles for source of data.
    '''
    __tablename__ = 'vehicles'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    type = Column(String(5), nullable=False)
    nation = Column(String(10), nullable=False)
    tier = Column(Integer, nullable=False)


class VehicleStatsRow(Base):
    '''Represents a vehicle statistics database table row.

    See https://developers.wargaming.net/reference/all/wot/tanks/stats for source of data.
    '''
    __tablename__ = 'vehicle_stats'

    idx = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    tank_id = Column(Integer, nullable=False)
    avg_damage_blocked = Column(Float, nullable=False)                # Average damage blocked by armor per battle
    battle_avg_xp = Column(Integer, nullable=False)                   # Average experience per battle
    battles = Column(Integer, nullable=False)                         # Battles fought
    capture_points = Column(Integer, nullable=False)                  # Base capture points
    damage_dealt = Column(Integer, nullable=False)                    # Damage caused
    damage_received = Column(Integer, nullable=False)                 # Damage received
    direct_hits_received = Column(Integer, nullable=False)            # Direct hits received
    draws = Column(Integer, nullable=False)                           # Draws
    dropped_capture_points = Column(Integer, nullable=False)          # Base defense points
    explosion_hits = Column(Integer, nullable=False)                  # Hits on enemy as a result of splash damage
    explosion_hits_received = Column(Integer, nullable=False)         # Hits received as a result of splash damage
    frags = Column(Integer, nullable=False)                           # Vehicles destroyed
    hits = Column(Integer, nullable=False)                            # Hits
    hits_percents = Column(Integer, nullable=False)                   # Hit ratio
    losses = Column(Integer, nullable=False)                          # Defeats
    no_damage_direct_hits_received = Column(Integer, nullable=False)  # Direct hits received that caused no damage
    piercings = Column(Integer, nullable=False)                       # Penetrations
    piercings_received = Column(Integer, nullable=False)              # Penetrations received
    shots = Column(Integer, nullable=False)                           # Shots fired
    spotted = Column(Integer, nullable=False)                         # Enemies spotted
    survived_battles = Column(Integer, nullable=False)                # Battles survived
    tanking_factor = Column(Float, nullable=False)                    # damage blocked by armor / damage received
    wins = Column(Integer, nullable=False)                            # Victories
    xp = Column(Integer, nullable=False)                              # Total experience


class Vehicles(object):
    '''Class for operations on database vehicles and vehicle_stats tables.
    
    Args:
        wot (<class 'wargaming.WoT'>): base class for operations on wargaming.net API.
        account_id (int): the current account id.
    '''

    @property
    def wot(self):
        '''<class 'wargaming.WoT'>: base class for operations on wargaming.net API.'''
        return self._wot

    @property
    def account_id(self):
        '''int: the current account id.'''
        return self._account_id

    @property
    def engine(self):
        '''<sqlalchemy.Engine>: sqlalchemy database engine.'''
        return self._engine

    def add_vehicle_stats(self, tank_id):
        '''Adds a timestamped vehicle stats row to dadabase table vehicke_statss for this tank_id.
        
        Args:
            tank_id (int): retrieve data from wargaming.net API for this tank id.
        '''
        add_session = sessionmaker(bind=self.engine)()
        all_stats = self.wot.tanks.stats(account_id=self.account_id, fields="all", tank_id=tank_id)
        stats = all_stats[self.account_id][0]['all']
        vehicle_stats_row = VehicleStatsRow(
            idx=int(time.time() * 1000000),
            tank_id=tank_id,
            avg_damage_blocked=stats['avg_damage_blocked'],
            battle_avg_xp=stats['battle_avg_xp'],
            battles=stats['battles'],
            capture_points=stats['capture_points'],
            damage_dealt=stats['damage_dealt'],
            damage_received=stats['damage_received'],
            direct_hits_received=stats['direct_hits_received'],
            draws=stats['draws'],
            dropped_capture_points=stats['dropped_capture_points'],
            explosion_hits=stats['explosion_hits'],
            explosion_hits_received=stats['explosion_hits_received'],
            frags=stats['frags'],
            hits=stats['hits'],
            hits_percents=stats['hits_percents'],
            losses=stats['losses'],
            no_damage_direct_hits_received=stats['no_damage_direct_hits_received'],
            piercings=stats['piercings'],
            piercings_received=stats['piercings_received'],
            shots=stats['shots'],
            spotted=stats['spotted'],
            survived_battles=stats['survived_battles'],
            tanking_factor=stats['tanking_factor'],
            wins=stats['wins'],
            xp=stats['xp'])
        add_session.merge(vehicle_stats_row)
        add_session.commit()

    @staticmethod
    def _init_engine():
        '''Initialize the sql database engine.
        
        Returns:
            <sqlalchemy.Engine>: this sqlalchemy datavase engine.
        '''
        engine = create_engine(DB, echo=True)
        session = scoped_session(sessionmaker(autoflush=True, autocommit=False))
        session.configure(bind=engine)
        Base.metadata.create_all(engine)
        return engine

    def _init_vehicles_table(self):
        '''Collect account-specific vehicle data for specified fields, insert or merge to database.
        
        Structure of 'vehicles':
            dict: 'field' data for each 'tank_id' in account_id. {'tank_id': {'field': data, ...}, ...}
        '''
        account_vehicles = self.wot.account.tanks(account_id=self.account_id, fields="tank_id")
        account_vehicle_ids = [x['tank_id'] for x in account_vehicles[self.account_id]]
        str_account_vehicle_ids = [str(x) for x in account_vehicle_ids]
        tank_data = self.wot.encyclopedia.vehicles(fields='type, name, nation, tier')
        vehicles = {tank_id: tank_data[tank_id] for tank_id in tank_data.keys() if tank_id in str_account_vehicle_ids}
        add_session = sessionmaker(bind=self.engine)()
        for tank_id in vehicles:
            name_db = vehicles[tank_id]['name']
            type_db = TYPE_MAP[vehicles[tank_id]['type']]
            nation_db = NATION_MAP[vehicles[tank_id]['nation']]
            tier_db = vehicles[tank_id]['tier']
            vehicles_row = VehiclesRow(id=tank_id, name=name_db, type=type_db, nation=nation_db, tier=tier_db)
            add_session.merge(vehicles_row)
        add_session.commit()

    def __init__(self, wot, account_id):
        self._wot = wot
        self._account_id = account_id
        self._engine = self._init_engine()
        self._init_vehicles_table()
