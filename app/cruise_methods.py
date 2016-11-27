from app import db, Port, Cruise, Room, Price
from datetime import datetime as dt
import web_scrape as ws


def createroom(sailing_availability):
    sailing_id = sailing_availability['sailingId']
    available_staterooms = sailing_availability['startingFromPriceByPartyMix'][0]['stateroomTypes']

    # grab cruise based on sailing ID that these rooms will be conencted to
    cruise = Cruise.query.filter_by(sailing_id=sailing_id).first()

    # iterate through all rooms (inside, ocean view, etc)
    for item in available_staterooms:
        # iterate through all subtypes of rooms (mainly location: aft, mid, forward)
        for subtype in item['stateroomSubTypes']:
            id = subtype['id'].split(';')[0].split('-', 1)
            t = id[1]
            ship = id[0]

            # if there is an error then the room is not available
            if 'error' in subtype:
                location = "Unknown"
                price = "NULL"
                category = subtype['error']['typeId']
                name = sailing_id + "-" + ship + "-" + t + "-" + location + "-" + category
                r = Room(name, t, location, price, category, sailing_id, ship)
                r.prices.append(Price(price, dt.now()))
                db.session.add(r)
                cruise.rooms.append(r)
                #print "room error, unavailable"

            # parse regular room type
            elif subtype['startingFromPrice']['offerType'] == 'REGULAR':
                for details in subtype['locations']:
                    location = details['id']
                    price = details['startingFromPrice']['price']['summary']['total']
                    category = details['startingFromPrice']['stateroomCategory'].split(';')[0].split('-', 1)[1]
                    name = sailing_id + "-" + ship + "-" + t + "-" + location + "-" + category
                    #print details['startingFromPrice']['price']['summary']
                    r = Room(name, t, location, price, category, sailing_id, ship)
                    r.prices.append(Price(price, dt.now()))
                    db.session.add(r)
                    cruise.rooms.append(r)

            # Room without specified location and is there is a "guareentee" you will get a room
            elif subtype['startingFromPrice']['offerType'] == 'GTY' or subtype['startingFromPrice']['offerType'] == "IGT_OGT_VGT":
                location = "Unknown"
                price = subtype['startingFromPrice']['price']['summary']['total']
                category = subtype['startingFromPrice']['stateroomCategory'].split(';')[0].split('-', 1)[1]
                name = sailing_id + "-" + ship + "-" + t + "-" + location + "-" + category
                r = Room(name, t, location, price, category, sailing_id, ship)
                r.prices.append(Price(price, dt.now()))
                db.session.add(r)
                cruise.rooms.append(r)
            else:
                print "new subtype: " + str(subtype)

    db.session.commit()


def createcruise(cruise_sailing):
    name = ''
    destination = ''
    #ports = cruise_sailing['portsOfCall']
    sail_from_date = ""
    sail_to_date = ""
    ship = ""
    minage = None
    sailing_id = ""

    cruise_port_ids = checkports(cruise_sailing['ports'])  # create/add ports to db if not existing already

    # parse destinations for cruise
    for item in cruise_sailing['destinations']:
        destination = cruise_sailing['destinations'][str(item)]['name']

    # parse cruise name
    for item in cruise_sailing['products']:
        name = cruise_sailing['products'][str(item)]['name']

    # parse dates, minimum age, sailing id
    for item in cruise_sailing['sailings']:
        i = cruise_sailing['sailings'][str(item)]
        sail_from_date = dt.strptime(i['sailDateFrom'], "%Y-%m-%d")
        sail_to_date = dt.strptime(i['sailDateTo'], "%Y-%m-%d")
        if i['minimumTravelAgeInDays']:
            minage = i['minimumTravelAgeInDays']
        sailing_id = i['id'].split(";")[0]

    # parse ship name/abbreviation
    for item in cruise_sailing['ships']:
        ship = cruise_sailing['ships'][str(item)]['name']

    # create cruise object and add to DB
    cruise = Cruise(name, destination, sail_from_date, sail_to_date, ship, sailing_id, minimum_age=minage)
    db.session.add(cruise)

    # assign ports to cruise
    for p in cruise_port_ids:
        s = Port.query.get(p)
        cruise.ports_of_call.append(s)

    # commit DB changes and return cruise object
    db.session.commit()
    return cruise


def checkports(ports):
    p_objects = []

    for item in ports:
        i = ports[str(item)]['id'].split(";")[0]
        name = ports[str(item)]['name']
        location = None
        if ',' in name:
            name, location = name.rsplit(', ', 1)

        value = db.session.query(Port.p_id).filter_by(name=name).first()
        if value:
            p_objects.append(value.p_id)
        else:
            p = Port(name, i, location)
            db.session.add(p)
            db.session.commit()
            p_objects.append(p.p_id)

    return p_objects


def cruiseexists(id):
    return True if Cruise.query.filter_by(sailing_id=id).first() else False


def get_cruise(id):

    url, pdata = ws.generatepostdataandurl(str(id))

    return ws.getjsonfrompost(url, pdata, ws.auth_token)


def get_new_cruises():
    ids = ws.getalllistingids(ws.auth_token)

    for id in ids:

        if not cruiseexists(id):

            j = get_cruise(id)

            try:
                createcruise(j["cruise-sailing"])
            except Exception as e:
                print e
                print j
            try:
                createroom(j["sailing-availability"])
            except Exception as e:
                print e
                print j

            print "created objects for cruise and room for id: " + id
        else:

            print "cruise exists: " + id


def update_cruise_pricing(sailing_id):

    # get latest cruise JSON from the web
    j = get_cruise(sailing_id)

    # grab all rooms with the same sailing id


    #debug print rooms and prices
    # for room in rooms:
    #     print str(room.name) + " : " + str(room.price)

    sailing_id = j["sailing-availability"]['sailingId']
    available_staterooms = j["sailing-availability"]['startingFromPriceByPartyMix'][0]['stateroomTypes']

    # iterate through all rooms (inside, ocean view, etc)
    for item in available_staterooms:
        # iterate through all subtypes of rooms (mainly location: aft, mid, forward)
        for subtype in item['stateroomSubTypes']:
            id = subtype['id'].split(';')[0].split('-', 1)
            t = id[1]
            ship = id[0]

            # if there is an error then the room is not available
            if 'error' in subtype:
                location = "N/A"
                price = "NULL"
                category = subtype['error']['typeId']
                name = sailing_id + "-" + ship + "-" + t + "-" + location + "-" + category
                room = Room.query.filter_by(name=name).first()
                if str(room.price) != str(price):
                    room.prices.append(Price(room.price, dt.now()))
                    room.price = price
                    print "DIFFERENCE! detected. Current: " + str(room.price) + " New: " + price

            # parse regular room type
            elif subtype['startingFromPrice']['offerType'] == 'REGULAR':
                for details in subtype['locations']:
                    location = details['id']
                    price = details['startingFromPrice']['price']['summary']['total']
                    category = details['startingFromPrice']['stateroomCategory'].split(';')[0].split('-', 1)[1]
                    name = sailing_id + "-" + ship + "-" + t + "-" + location + "-" + category
                    room = Room.query.filter_by(name=name).first()
                    if str(room.price) != str(price):
                        print "DIFFERENCE! detected. Current: " + str(room.price) + " New: " + price
                        room.prices.append(Price(room.price, dt.now()))
                        room.price = price
                        # FIGURE OUT IF PRICE RELATIONSHIP WORKS
                        # IF IT DOES, WORK ON TESTING NEW PRICES

            # Room without specified location and is there is a "guareentee" you will get a room
            elif subtype['startingFromPrice']['offerType'] == 'GTY' or subtype['startingFromPrice'][
                'offerType'] == "IGT_OGT_VGT":
                location = "Unknown"
                price = subtype['startingFromPrice']['price']['summary']['total']
                category = subtype['startingFromPrice']['stateroomCategory'].split(';')[0].split('-', 1)[1]
                name = sailing_id + "-" + ship + "-" + t + "-" + location + "-" + category
                room = Room.query.filter_by(name=name).first()
                if str(room.price) != str(price):
                    print "DIFFERENCE! detected. Current: " + str(room.price) + " New: " + price
                    room.prices.append(Price(room.price, dt.now()))
                    room.price = price
            else:
                print "new subtype: " + str(subtype)
    db.session.commit()



    # compare rooms in json to rooms in DB
        # if type changes.... not sure
    # if price changes take current price and put in price_over_time table
    # update price in rooms table with new price



#update_all_cruises()

#update_cruise_pricing("DD0647")

# room = Room.query.filter_by(sailing_id="DD0647").first()
# print room.price
# room.prices.append(Price(1900, dt.now()))
#
#
# for p in room.prices:
#     print p.price
# print Price.query.filter_by(price=1900).first().change_date

# PRICE RELATIONSHIP TESTING^^^^