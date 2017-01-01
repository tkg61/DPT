import lxml.html as lh
import requests
from datetime import datetime as dt, timedelta
import itertools

html = open("..\Datafiles\Southwest_test.html", 'r').read()


def get_flight_info(html, return_or_outbound):
    flight_info = {}
    in_out = return_or_outbound
    html = lh.fromstring(html)

    if return_or_outbound == "outbound":
        faretype = "Outbound"
        abbr = "Out"
    else:
        faretype = "Return"
        abbr = "In"

    for tr in html.xpath('//*[@id="fares' + faretype + '"]/tbody/tr'):
        fnum = tr.xpath('@id')[0].split("_")[2]
        price_a = html.xpath('// *[ @ id = "' + abbr + fnum + 'AContainer"] / div / div[2] / div / label[1] / text()')
        price_b = html.xpath('// *[ @ id = "' + abbr + fnum + 'BContainer"] / div / div[2] / div / label[1] / text()')
        price_c = html.xpath('// *[ @ id = "' + abbr + fnum + 'CContainer"] / div / div[2] / div / label[1] / text()')
        price_a = "Sold Out" if not price_a else int(price_a[1].strip())
        price_b = "Sold Out" if not price_b else int(price_b[1].strip())
        price_c = "Sold Out" if not price_c else int(price_c[1].strip())
        departure_time = html.xpath('//*[@id="' + in_out + '_flightRow_' + fnum + '"]/td[1]/div[2]/span/span[1]/text()')[0].strip()  # dept
        departure_am_pm = html.xpath('//*[@id="' + in_out + '_flightRow_' + fnum + '"]/td[1]/div[2]/span/span[2]/text()')[0].strip()  # dept_am_pm
        arrival_time = html.xpath('//*[@id="' + in_out + '_flightRow_' + fnum + '"]/td[2]/div/span/span[1]/text()')[0].strip()  # arrival
        arrival_am_pm = html.xpath('//*[@id="' + in_out + '_flightRow_' + fnum + '"]/td[2]/div/span/span[2]/text()')[0].strip()  # arrival_am_pm
        flight_num = map(str.strip, html.xpath('//*[@id="' + in_out + '_flightRow_' + fnum + '"]/td[3]/div/span/span/span[2]/a/text()'))  # flight num
        num_of_stops = html.xpath('//*[@id="' + in_out + '_flightRow_' + fnum + '"]/td[4]/div/span[2]/a/text()')[0].strip()  # num of stops
        location_of_stops = html.xpath('//*[@id="' + in_out + '_flightRow_' + fnum + '"]/td[4]/div/span[3]/text()')[0].strip() # location of plane change or no plane change
        flight_time_hour = html.xpath('//*[@id="' + in_out + '_flightRow_' + fnum + '"]/td[5]/div/span/text()[1]')[0].strip() # duration - Hour
        flight_time_min = html.xpath('//*[@id="' + in_out + '_flightRow_' + fnum + '"]/td[5]/div/span/text()[2]')[0].strip() # duration - minute
        flight_index = "_".join(flight_num) if len(flight_num) > 1 else flight_num[0].strip()
        flight_time = flight_time_hour + ":" + flight_time_min

        depart = dt.strptime(departure_time+departure_am_pm, '%I:%M%p')
        arrive = dt.strptime(arrival_time + arrival_am_pm, '%I:%M%p')
        if departure_am_pm == "PM" and arrival_am_pm == "AM":
            arrive = arrive + timedelta(days=1)
            print"there was a next day flight: " + str(flight_num)

        flight_info[flight_index] = [depart, arrive, flight_num, num_of_stops, location_of_stops, flight_time, price_a,
                                     price_b, price_c]
        # print price_a
        # print price_b
        # print price_c
        # print departure_time
        # print arrival_time
        # print flight_num
        # print num_of_stops
        # print location_of_stops
        # print flight_time_hour
        # print flight_time_min
        # print "\r"
    return flight_info


def get_html(airport_from, airport_to, depart_date, return_date, roundtrip=True):
    url = "https://www.southwest.com/flight/search-flight.html"
    cont = True
    try:
        d_month, d_day, d_year = depart_date.split("-")
        r_month, r_day, r_year = return_date.split("-")
    except:
        print("date was not splittable")
        cont = False

    if cont:
        payload = 'twoWayTrip=' + str(roundtrip) + '&originAirport=' + airport_from + '&destinationAirport=' + airport_to + \
                  '&airTranRedirect=&returnAirport=RoundTrip&outboundDateString=' + d_month + '%2F' + d_day + '%2F' +\
                  d_year + '&outboundTimeOfDay=ANYTIME&returnDateString=' + r_month + '%2F' + r_day + '%2F' +\
                  r_year + '&returnTimeOfDay=ANYTIME&adultPassengerCount=2&seniorPassengerCount=0&fareType=DOLLARS'
        headers = {
                    'content-type': "application/x-www-form-urlencoded",
                    'cache-control': "no-cache"
                  }

        response = requests.request("POST", url, data=payload, headers=headers)

        return response.text
    else:
        return None


def find_cheap_flights(flights_dict, depart_after=None, depart_before=None, arrive_after=None, arrive_before=None,
                       highest_price=100000, nonstop=True, max_travel_time=None, relaxed=False):
    #depart_by, arrive_by = (dt.now(), dt.now()) if not depart_by and not arrive_by else dt.strptime(depart_by, '%I:%M%p'), dt.strptime(arrive_by, '%I:%M%p')

    depart_after = dt.now() if not depart_after else dt.strptime(depart_after, '%I:%M%p')
    depart_before = dt.now() if not depart_before else dt.strptime(depart_before, '%I:%M%p')
    arrive_before = dt.now() if not arrive_before else dt.strptime(arrive_before, '%I:%M%p')
    arrive_after = dt.now() if not arrive_after else dt.strptime(arrive_after, '%I:%M%p')


    best_flight = [dt.now(), dt.now(), '', nonstop, '', max_travel_time, highest_price, highest_price, highest_price]
    best_matched = [None, None, None, None, None, None, None, None, None]
    best_score = 0
    new_best = True

    while new_best:
        print ("New best found --------------------------")
        for flight_index, flight in flights_dict.iteritems():
            score = 0
            matched = [None, None, None, None, None, None, None, None, None]
            if flight[8] != 'Sold Out':
                if relaxed and int(flight[8]) in range(int(best_flight[8]), (int(best_flight[8]) + relaxed)):
                    # print range(int(best_flight[8]), (int(best_flight[8]) + 20))
                    score += 2 if highest_price != 100000 else 1
                    print("price in range")
                elif flight[8] <= best_flight[8]:
                    score += 2 if highest_price != 100000 else 1
                    print("better price" + str(score))

                if depart_after:
                    if depart_after < flight[0]:
                        score += 1 if depart_after.day is not dt.now().day else 0
                        if flight[0] < best_flight[0]:
                            score += 1 if depart_after.day is not dt.now().day else 0
                        print("better depart_after: " + str(score))
                    # else:
                    #     score -= 2
                    #     print("worse depart_after: " + str(score))
                if depart_before and depart_before > flight[0]:
                    score += 1 if depart_before.day is not dt.now().day else 0
                    print("better depart before")
                if arrive_after and arrive_after < flight[1]:
                    score += 1 if arrive_after.day is not dt.now().day else 0
                    print("better arrive after")
                if arrive_before and arrive_before > flight[1]:
                    score += 1 if arrive_before.day is not dt.now().day else 0
                    if flight[1] < best_flight[1]:
                        score += 1 if arrive_before.day is not dt.now().day else 0
                    print("better arrival_before")

                if nonstop and flight[3] == "Nonstop":
                    score += 1
                    print("nonstop")
                else:
                    score += 0 if nonstop else 1

                if flight[5] <= best_flight[5]:
                    score += 2 if flight[5] < max_travel_time else 1
                    print ("better time")

                print best_flight
                print score
                print flight
                if score > best_score:
                    best_flight = flight
                    best_score = score
                    new_best = True
                    break
                else:
                    new_best = False

    print best_score
    print "\r"
    return best_flight


html = get_html("BWI", "MCO", "05-23-2017", "05-31-2017")
outbound = get_flight_info(html, "outbound")
#return_flight = get_flight_info(html, "inbound")

print outbound
#print return_flight

#print find_cheap_flights(outbound, arrive_before="12:31PM", highest_price=100)
#print find_cheap_flights(return_flight, depart_after="12:31PM", arrive_before="11:59PM", highest_price=100)


def test_find(flights_dict, depart_after=None, depart_before=None, arrive_after=None, arrive_before=None,
                       highest_price=100000, nonstop=True, max_travel_time=None, relaxed=False):
    #depart_by, arrive_by = (dt.now(), dt.now()) if not depart_by and not arrive_by else dt.strptime(depart_by, '%I:%M%p'), dt.strptime(arrive_by, '%I:%M%p')

    depart_after = dt.strptime(depart_after, '%I:%M%p') if depart_after else None
    depart_before = dt.now() if not depart_before else dt.strptime(depart_before, '%I:%M%p')
    arrive_before = dt.strptime(arrive_before, '%I:%M%p') if arrive_before else None
    arrive_after = dt.now() if not arrive_after else dt.strptime(arrive_after, '%I:%M%p')

    test_dict = {}
    best_dict = {}

    for flight_index, flight in flights_dict.iteritems():
        items_matched = dict()
        items_matched['price'] = 1 if highest_price and flight[8] < highest_price else 0
        items_matched['depart_after'] = 1 if depart_after and flight[0] > depart_after else 0
        items_matched['arrive_before'] = 1 if arrive_before and flight[1] < arrive_before else 0
        items_matched['flight_time'] = 1 if max_travel_time and flight[5] < max_travel_time else 0
        items_matched['nonstop'] = 1 if nonstop and flight[3] == "Nonstop" else 0
        items_matched['not_nonstop'] = 1 if not nonstop and flight[3] != "Nonstop" else 0

        test_dict[flight_index] = items_matched

    for index, f in test_dict.iteritems():
        amount = {k: len(list(v)) for k, v in itertools.groupby(sorted(f.values()))}
        print index
        print amount
        if amount[0] is not 6:
            best_dict[index] = amount[1]

    best_flight = max(best_dict.iterkeys(), key=(lambda key: best_dict[key]))
    print best_flight
    print test_dict[best_flight]

test_find(outbound, arrive_before="12:31PM", highest_price=100)
