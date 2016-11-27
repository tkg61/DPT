import requests
from datetime import datetime as dt, timedelta as td
import time

auth_token = ''
token_expires = None
post_retry = 1

def generatepostdataandurl(id, adultcount=2, childcount=0, nonadultages=None, currency='USD'):
    if not nonadultages:
        nonadultages = []

    url = 'https://disneycruise.disney.go.com/wam/cruise-sales-service/view-assembly/' \
                             'cruise-sailings/' + id + ';entityType=cruise-sailing;destination=dcl?region=INTL' \
                             '&view=select-stateroom'
    return url, {"affiliations": [], "region": "INTL", "sailingId": id + ";entityType=cruise-sailing;destination=dcl",
            "partyMix": [{"accessible": 'false', "partyMixId": 0, "orderBuilderId": "null", "adultCount": adultcount,
            "childCount": childcount, "nonAdultAges": nonadultages}], "currency": currency}


def refresh_token():
    global auth_token
    global token_expires

    # return json object with "access_token" and "expires_in" fields (seconds)
    if has_token_expired():
        try:
            r = requests.get("https://disneycruise.disney.go.com/wam/authentication/get-client-token/").json()  # GET token
            auth_token = r["access_token"]
            token_expires_seconds = r['expires_in']

            token_expires = dt.now() + td(seconds=int(token_expires_seconds))

            print "Refreshed token successfully. Expires: " + str(token_expires)
            return True
        except Exception as e:
            print str(e)
            return False
            # return re.search('token=(.*?);', r.headers['Set-Cookie']).group(1) # get oauth token from cookie in header


def has_token_expired():
    # giving a cushion of 30 seconds before actual expiration
    return False if token_expires and (dt.now() + td(seconds=60)) < token_expires else True


def getjsonfrompost(url, data, token=None):
    global post_retry

    if token:
        headers = {'Content-Type': "application/json",
                   'Authorization': "BEARER " + token}
        j = requests.post(url, json=data, headers=headers).json()
    else:
        j = requests.post(url, json=data).json()

    while post_retry < 4:
        if 'err' in j:
            print "Token expired?: " + str(has_token_expired())
            if has_token_expired():
                refresh_token()
            print "Retrying query " + str(post_retry) + " of 3 times..."

            post_retry += 1
            j = getjsonfrompost(url, data, auth_token)  # retry getting data
        else:
            post_retry = 1
            break

    return j


def getalllistingids(token):
    url = 'https://disneycruise.disney.go.com/wam/cruise-sales-service/cruise-listing/?region=INTL&storeId=DCL&view=cruise-listing'
    data = {"currency": "USD", "affiliations": [], "partyMix": [{"accessible": "false", "adultCount":2, "childCount": 0,
                                                                 "orderBuilderId": "null", "nonAdultAges":[],
                                                                 "partyMixId":"0"}]}

    j = getjsonfrompost(url, data, token)

    listings = []

    if 'err' not in j:
        for listing in j['sailings-availability']['sailings']:
            listings.append(j['sailings-availability']['sailings'][str(listing)]['sailingId'].split(';')[0])

    return listings


#t = gettoken()["access_token"]


#ids = ['DM1062']

#c = cm.Cruise.query.filter_by(sailing_id=ids[0]).first()
# print c.name
#
# for r in c.rooms:
#     print str(r.name) + " " + str(r.price)





