'''Module to collect relevant data from wargaming.net, merge into database & provide database services.
'''
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, exc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from datetime import datetime
import wargaming
import logging
from constants import SUCCESS, FAILURE, DEFAULT_DB, VEHICLE_FIELDS, TYPE_MAP, NATION_MAP

Base = declarative_base()


class VehiclesRow(Base):
    '''Represents a vehicles database table row.
    
    See https://developers.wargaming.net/reference/all/wot/encyclopedia/vehicles for source of data.
    '''
    __tablename__ = 'vehicles'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    type = Column(String(50), nullable=False)
    nation = Column(String(50), nullable=False)
    tier = Column(Integer, nullable=False)


class VehicleStatsRow(Base):
    '''Represents a vehicle statistics database table row.

    See https://developers.wargaming.net/reference/all/wot/tanks/stats for source of data.
    '''
    __tablename__ = 'vehicle_stats'

    id = Column(Integer, primary_key=True)
    tank_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    timestamp_utc = Column(DateTime, nullable=False, default=datetime.utcnow)
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
    def status(self):
        '''int: current class operation status, SUCCESS or FAILURE.'''
        return self._status

    @property
    def wot(self):
        '''<class 'wargaming.WoT'>: base class for operations on wargaming.net API.'''
        return self._wot

    @property
    def account_id(self):
        '''int: the current account id.'''
        return self._account_id

    @property
    def account_vehicle_ids(self):
        '''list[int]: all vehicle ids belonging to specified account.'''
        return self._account_vehicle_ids

    @property
    def engine(self):
        '''<sqlalchemy.Engine>: sqlalchemy database engine.'''
        return self._engine

    def current_vehicle_stats(self, tank_id):
        '''Adds a timestamped this tank_id vehicle stats row to database table vehicle_stats.
        
        Args:
            tank_id (int): retrieve data from wargaming.net API for this tank id.
        Exceptions:
            exc.SQLAlchemyError: base sqlalchemy exception class.
        '''
        msg = ''
        prefix = 'current_vehicle_stats(): '
        if self.status == FAILURE:
            msg = '{} exiting, invalid Vehicles class'.format(prefix)
        elif tank_id not in self.account_vehicle_ids:
            msg = '{} exiting, vehicle id {} not found for account id {}'.format(prefix, tank_id, self.account_id)
        if msg != '':
            logging.error(msg)
            return
        merge_session = sessionmaker(bind=self.engine)()
        all_stats = self.wot.tanks.stats(account_id=self.account_id, fields="all", tank_id=tank_id)
        stats = all_stats[self.account_id][0]['all']
        vehicle_stats_row = VehicleStatsRow(
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
        merge_session.merge(vehicle_stats_row)
        try:
            merge_session.commit()
        except exc.SQLAlchemyError as e:
            msg = '{} {}'.format(prefix, e.message)
            logging.error(msg)
            self._status = FAILURE

    @staticmethod
    def _init_engine():
        '''Initialize the sql database engine.
        
        Returns:
            <sqlalchemy.Engine>: this sqlalchemy database engine.
        '''
        engine = create_engine(DEFAULT_DB, echo=True)
        session = scoped_session(sessionmaker(autoflush=True, autocommit=False))
        session.configure(bind=engine)
        Base.metadata.create_all(engine)
        return engine

    def _merge_data_vehicle_table(self, vehicles):
        '''Add or merge the vehicle data into the Vehicles database table.
        
        Args:
            vehicles (dict): 'field' data for each 'tank_id' in account_id. {'tank_id': {'field': data, ...}, ...}.
        Exceptions:
            exc.SQLAlchemyError: base sqlalchemy exception class.
        '''
        prefix = 'merge_data_vehicle_table(): '
        if self.status == FAILURE:
            msg = '{} exiting, invalid Vehicles class'.format(prefix)
            logging.error(msg)
            return
        merge_session = sessionmaker(bind=self.engine)()
        for tank_id in vehicles:
            vehicle = vehicles[tank_id]
            vehicles_row = VehiclesRow(
                id=int(tank_id),
                name=vehicle['name'],
                type=TYPE_MAP.get(vehicle['type'], 'unknown'),
                nation=NATION_MAP.get(vehicle['nation'], 'unknown'),
                tier=vehicle['tier'])
            merge_session.merge(vehicles_row)
        try:
            merge_session.commit()
        except exc.SQLAlchemyError as e:
            msg = '{} {}'.format(prefix, e.message)
            logging.error(msg)
            self._status = FAILURE

    def _get_vehicle_data(self):
        '''Get vehicle VEHICLE_FIELD data for current account vehicles.

        Returns:
            dict: 'field' data for each 'tank_id' in account_id. {'tank_id': {'field': data, ...}, ...}.
        Exceptions:
            wargaming.exceptions.RequestError if Wargaming API returns error.
            wargaming.exceptions.ValidationError if invalid param value error.
        '''
        prefix = 'get_vehicles(): '
        msg = ''
        vehicles = {}
        if self.status == FAILURE:
            msg = '{} exiting, invalid Vehicles class'.format(prefix)
            logging.error(msg)
            return vehicles
        try:
            v_data = self.wot.encyclopedia.vehicles(fields=VEHICLE_FIELDS)
        except wargaming.exceptions.RequestError as e:
            msg = '{} RequestError {} {} {} {}'.format(prefix, e.code, e.field, e.message, e.value)
        except wargaming.exceptions.ValidationError as e:
            msg = '{} ValidationError {}'.format(prefix, e.message)
        else:
            vehicles = {vid: v_data[vid] for vid in v_data.keys() if int(vid) in self.account_vehicle_ids}
        finally:
            if msg != '':
                logging.error(msg)
                self._status = FAILURE
        return vehicles

    def _get_account_vehicle_ids(self):
        '''Get the vehicle ids belonging to the current account.
        
        Returns:
            list[int]: all vehicle ids belonging to specified account or empty list.
        Exceptions:
            wargaming.exceptions.RequestError if Wargaming API returns error.
            wargaming.exceptions.ValidationError if invalid param value error.
        '''
        prefix = 'get_account_vehicle_ids(): '
        msg = ''
        account_vehicle_ids = []
        if self.status == FAILURE:
            msg = '{} exiting, invalid Vehicles class'.format(prefix)
            logging.error(msg)
            return account_vehicle_ids
        try:
            account_vehicles = self.wot.account.tanks(account_id=self.account_id, fields="tank_id")
        except wargaming.exceptions.RequestError as e:
            msg = '{} RequestError {} {} {} {}'.format(prefix, e.code, e.field, e.message, e.value)
        except wargaming.exceptions.ValidationError as e:
            msg = '{} ValidationError {}'.format(prefix, e.message)
        else:
            account_vehicle_ids = [x['tank_id'] for x in account_vehicles[self.account_id]]
        finally:
            if msg != '':
                logging.error(msg)
                self._status = FAILURE
            return account_vehicle_ids

    def __init__(self, wot, account_id):
        self._status = SUCCESS
        self._wot = wot
        self._account_id = account_id
        self._engine = self._init_engine()
        self._account_vehicle_ids = self._get_account_vehicle_ids()
        self._merge_data_vehicle_table(self._get_vehicle_data())
