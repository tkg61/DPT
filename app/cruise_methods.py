from models import Room, Cruise, Port
from app import db
from datetime import datetime as dt
from app import web_scrape as ws

def createroom(sailing_availability):
    sailing_id = sailing_availability['sailingId']
    available_staterooms = sailing_availability['startingFromPriceByPartyMix'][0]['stateroomTypes']

    # grab cruise based on sailing ID that these rooms will be conencted to
    cruise = Cruise.query.filter_by(sailing_id=sailing_id).first()

    # iterate through all rooms (inside, ocean view, etc)
    for item in available_staterooms:
        # iterate through all subtypes of rooms (mainly location, aft, mid, forward)
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
                    db.session.add(r)
                    cruise.rooms.append(r)

            # Room without specified location and is ther is a "guareentee" you will get a room
            elif subtype['startingFromPrice']['offerType'] == 'GTY' or subtype['startingFromPrice']['offerType'] == "IGT_OGT_VGT":
                location = "Unknown"
                price = subtype['startingFromPrice']['price']['summary']['total']
                category = subtype['startingFromPrice']['stateroomCategory'].split(';')[0].split('-', 1)[1]
                name = sailing_id + "-" + ship + "-" + t + "-" + location + "-" + category
                r = Room(name, t, location, price, category, sailing_id, ship)
                db.session.add(r)
                cruise.rooms.append(r)
            else:

                print subtype

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
        print p
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
            print "port exists"
            p_objects.append(value.p_id)
        else:
            p = Port(name, i, location)
            db.session.add(p)
            db.session.commit()
            p_objects.append(p.p_id)

    return p_objects


def cruiseexists(id):
    return True if Cruise.query.filter_by(sailing_id=id).first() else False


def update_all_cruises(token):
    t = ws.gettoken()["access_token"]
    ids = ws.getalllistingids(t)

    for id in ids:

        if not cruiseexists(id):

            url, pdata = ws.generatepostdataandurl(str(id))

            print "got url for id: " + id

            j = ws.getjsonfrompost(url, pdata, t)

            if 'err' in j:
                while j['err']:
                    print "Token expired, getting a new one"
                    t = gettoken()["access_token"]

                    j = getjsonfrompost(url, pdata, t)  # retry getting data

            #print "got json for id: " + id

            try:
                cm.createcruise(j["cruise-sailing"])
            except Exception as e:
                print e
                print j
            try:
                cm.createroom(j["sailing-availability"])
            except Exception as e:
                print e
                print j

            print "created objects for cruise and room for id: " + id
        else:
            print "cruise exists: " + id
