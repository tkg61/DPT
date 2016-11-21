from flask_sqlalchemy import SQLAlchemy
from app import db
from datetime import datetime as dt

# region association tables
cruise_to_port = db.Table('cruise_to_port',
                          db.Column('c_id', db.Integer, db.ForeignKey('cruises.c_id')),
                          db.Column('p_id', db.Integer, db.ForeignKey('ports.p_id'))
                          )
cruise_to_room = db.Table('cruise_to_room',
                           db.Column('c_id', db.Integer, db.ForeignKey('cruises.c_id')),
                           db.Column('r_id', db.Integer, db.ForeignKey('rooms.r_id'))
                           )
# endregion


class Room(db.Model):
    __tablename__ = "rooms"
    # __metaclass__ = IterRoom
    # _roomlist  = []

    r_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))  # type + location + category
    type = db.Column(db.String(120))  # inside stateroom standard
    location = db.Column(db.String(120))  # forward, aft, mid
    price = db.Column(db.Integer)
    category = db.Column(db.String(120))  # 11b
    sailing_id = db.Column(db.String(120))
    ship = db.Column(db.String(120))

    _titles = {'INSIDE-STANDARD': 'Standard Inside Stateroom',
               'INSIDE-DELUXE': 'Deluxe Inside Stateroom',
               'OUTSIDE-DELUXE': 'Deluxe Oceanview Stateroom',
               'VERANDAH-DELUXEOCEANVIEW': 'Deluxe Oceanview Stateroom with Verandah',
               'VERANDAH-DELUXEFAMILY': 'Deluxe Family Oceanview Stateroom with Verandah',
               'SUITE-CONCIERGE-ONE-BEDROOM': 'Concierge 1-Bedroom Suite with Verandah',
               'SUITE-CONCIERGE-TWO-BEDROOM': 'Concierge 2-Bedroom Suite with Verandah',
               'SUITE-CONCIERGE-ROYAL': 'Concierge Royal Suite with Verandah',
               'VERANDAH-VGT': 'Guaranteed Verandah Stateroom with Restrictions',
               'INSIDE-IGT': 'Guaranteed Inside Stateroom with Restrictions',
               'OUTSIDE-OGT': 'Guaranteed Oceanview Stateroom with Restrictions'}
    _ships = {'DM': 'Disney Magic',
              'DW': 'Disney Wonder',
              'DF': 'Disney Fantasy',
              'DD': 'Disney Dream'
              }

    def __init__(self, name, t, location, price, category, sailing_id, ship, **kwargs):
        # self._roomlist.append(self)
        self.name = name  # type + location + category
        self.type = t  # inside stateroom standard
        self.location = location  # forward, aft, mid
        self.price = price
        self.category = category  # 11b
        self.sailing_id = sailing_id
        self.ship = ship

        for varname, value in kwargs.iteritems():
            setattr(self, varname, value)

    def title(self):
        if self.type in self._titles.keys():
            return self._titles[self.type]
        else:
            return self.type

    def view(self):
        return "awesome"
        # have different dictionary dynamically populated with categories 11b and the view

    # @classmethod
    # def classiter(cls):  # iterate over class by giving all instances which have been instantiated
    #     return iter(cls._roomlist)


class Cruise(db.Model):
    # __metaclass__ = IterCruise
    # _cruiselist = []
    __tablename__ = "cruises"

    c_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    destination = db.Column(db.String(120))
    ports_of_call = db.relationship("Port", secondary=cruise_to_port)
    rooms = db.relationship("Room", secondary=cruise_to_room)
    sail_from_date = db.Column(db.DateTime)
    sail_to_date = db.Column(db.DateTime)
    ship = db.Column(db.String(120))
    sailing_id = db.Column(db.String(120))

    def __init__(self, name, destination, sail_from_date, sail_to_date, ship, sailing_id, **kwargs):
        # self._cruiselist.append(self)
        self.name = name
        self.destination = destination
        #self.ports_of_call = ports_of_call
        self.sail_from_date = sail_from_date
        self.sail_to_date = sail_to_date
        self.ship = ship
        self.sailing_id = sailing_id

        for varname, value in kwargs.iteritems():
            setattr(self, varname, value)

    def cruiselength(self):
        return dt.strptime(self.sail_to_date, '%Y-%m-%d') - dt.strptime(self.sail_from_date, '%Y-%m-%d')

    def getrooms(self):
        for room in self.rooms:
            print room
        #return rooms


class Port(db.Model):
    __tablename__ = "ports"

    # Fields
    p_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    port_id = db.Column(db.Integer, unique=True)
    location = db.Column(db.String(120))

    def __init__(self, name, port_id, location):
        self.name = name
        self.port_id = port_id
        self.location = location