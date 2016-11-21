from datetime import datetime as dt


class IterRoom(type):  # allow for the list of rooms to be returned
    def __iter__(cls):
        return iter(cls._roomlist)


class Room(object):
    __metaclass__ = IterRoom
    _roomlist = []

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
        self._roomlist.append(self)  # add self to room list
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


# one = Room('DM-VERANDAH-DELUXEOCEANVIEW-MID-11b', "DM-VERANDAH-DELUXEOCEANVIEW", 'MID', 5000, "11b", "DM1076", "Disney Magic")
#
# print one.title()

class IterCruise(type):  # allow for the list of rooms to be returned
    def __iter__(cls):
        return iter(cls._cruiselist)


class Cruise(object):
    __metaclass__ = IterCruise
    _cruiselist = []

    def __init__(self, name, destination, ports_of_call, sail_from_date, sail_to_date, ship, sailing_id, **kwargs):
        self._cruiselist.append(self)
        self.name = name
        self.destination = destination
        self.ports_of_call = ports_of_call
        self.sail_from_date = sail_from_date
        self.sail_to_date = sail_to_date
        self.ship = ship
        self.sailing_id = sailing_id

        for varname, value in kwargs.iteritems():
            setattr(self, varname, value)

    def cruiselength(self):
        return dt.strptime(self.sail_to_date, '%Y-%m-%d') - dt.strptime(self.sail_from_date, '%Y-%m-%d')

    def getrooms(self):
        rooms = []
        for room in Room:
            if room.sailing_id == self.sailing_id:
                rooms.append(str(room.name))
        return rooms


