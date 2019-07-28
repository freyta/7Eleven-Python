#! /usr/bin/python3

#    7-Eleven Python implementation. This program allows you to lock in a fuel price from your computer.
#    Copyright (C) 2019  Freyta
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <https://www.gnu.org/licenses/>.

# Functions used for the TSSA generation
import hmac, base64, hashlib, uuid, time
# Needed for the VmobID
import pyDes
# Functions used for setting our currently locked in fuel prices to the correct timezone
import pytz, datetime
# Used for requests to the price check script and for 7-Eleven stores
import requests, json
# Functions used for getting the OS environments from settings.py
import settings, os
# Needed for our randomly generated Device ID
import random
# Needed so we can set flask session variables
from flask import session


'''''''''''''''''''''''''''
You can set or change any these environmental variables in settings.py
'''''''''''''''''''''''''''
API_KEY = os.getenv('API_KEY',settings.API_KEY)
TZ = os.getenv('TZ', settings.TZ)
BASE_URL = os.getenv('BASE_URL',settings.BASE_URL)
PRICE_URL = os.getenv('PRICE_URL',settings.PRICE_URL)
DEVICE_NAME = os.getenv('DEVICE_NAME', settings.DEVICE_NAME)
OS_VERSION = os.getenv('OS_VERSION', settings.OS_VERSION)
APP_VERSION = os.getenv('APP_VERSION', settings.APP_VERSION)

def getKey():
    # Found in file au.com.seveneleven.y.h
    a = [103, 180, 267, 204, 390, 504, 497, 784, 1035, 520, 1155, 648, 988, 1456, 1785]
    # Found in file au.com.seveneleven.x.a
    b = [50, 114, 327, 276, 525, 522, 371, 904, 1017, 810, 858, 852, 1274, 1148, 915]
    # Found in file au.com.seveneleven.x.c
    c = [74, 220, 249, 416, 430, 726, 840, 568, 1017, 700, 1155, 912, 1118, 1372]

    # Get the length of all 3 variables
    length = len(a) + len(b) + len(c)
    key = ""
    # Generate the key with a bit of maths
    for i in range(length):
        if(i % 3 == 0):
            key += chr( int((a[int(i / 3)] / ((i / 3) + 1)) ))
        if(i % 3 == 1):
            key += chr( int((b[int((i - 1) / 3)] / (((i - 1) / 3) + 1)) ))
        if(i % 3 == 2):
            key += chr( int((c[int((i - 1) / 3)] / (((i - 2) / 3) + 1)) ))

    return key

def generateTssa(URL, method, payload = None, accessToken = None):

    # Replace the https URL with a http one and convert the URL to lowercase
    URL       = URL.replace("https", "http").lower()
    # Get a timestamp and a UUID
    timestamp = int(time.time())
    uuidVar   = str(uuid.uuid4())
    # Join the variables into 1 string
    str3      = "yvktroj08t9jltr3ze0isf7r4wygb39s" + method + URL + str(timestamp) + uuidVar
    # If we have a payload to encrypt, then we encrypt it and add it to str3
    if(payload):
        payload = base64.b64encode(hashlib.md5(payload.encode()).digest())
        str3   += payload.decode()

    signature = base64.b64encode(hmac.new(encryption_key, str3.encode(), digestmod=hashlib.sha256).digest())

    # Finish building the tssa string
    tssa = "tssa yvktroj08t9jltr3ze0isf7r4wygb39s:" + signature.decode() + ":" + uuidVar + ":" + str(timestamp)
    # If we have an access token append it to the tssa string
    if(accessToken):
        tssa += ":" + accessToken

    return tssa

def cheapestFuelAll():
    # Just a quick way to get fuel prices from a website that is already created.
    # Thank you to master131 for this.
    r = requests.get(PRICE_URL)
    response = json.loads(r.text)

    # E10
    session['postcode0'] = response['regions'][0]['prices'][0]['postcode']
    session['price0']    = response['regions'][0]['prices'][0]['price']

    # Unleaded 91
    session['postcode1'] = response['regions'][0]['prices'][1]['postcode']
    session['price1']    = response['regions'][0]['prices'][1]['price']

    # Unleaded 95
    session['postcode2'] = response['regions'][0]['prices'][2]['postcode']
    session['price2']    = response['regions'][0]['prices'][2]['price']

    # Unleaded 98
    session['postcode3'] = response['regions'][0]['prices'][3]['postcode']
    session['price3']    = response['regions'][0]['prices'][3]['price']

    # Diesel
    session['postcode4'] = response['regions'][0]['prices'][4]['postcode']
    session['price4']    = response['regions'][0]['prices'][4]['price']

    # LPG
    session['postcode5'] = response['regions'][0]['prices'][5]['postcode']
    session['price5']    = response['regions'][0]['prices'][5]['price']

def cheapestFuel(fueltype):
    # Gets the cheapest fuel price for a certain type of fuel and the postcode
    # This is used for the automatic lock in
    r = requests.get(PRICE_URL)
    response = json.loads(r.text)
    '''
    52 = Unleaded 91
    53 = Diesel
    54 = LPG
    55 = Unleaded 95
    56 = Unleaded 98
    57 = E10
    '''
    if(fueltype == "52"):
        fueltype = 1
    if(fueltype == "53"):
        fueltype = 4
    if(fueltype == "54"):
        fueltype = 5
    if(fueltype == "55"):
        fueltype = 2
    if(fueltype == "56"):
        fueltype = 3
    if(fueltype == "57"):
        fueltype = 0

    # Get the postcode and price
    postcode  = response['regions'][0]['prices'][fueltype]['postcode']
    price     = response['regions'][0]['prices'][fueltype]['price']
    latitude  = response['regions'][0]['prices'][fueltype]['lat']
    longitude = response['regions'][0]['prices'][fueltype]['lng']
    return postcode, price, latitude, longitude

def lockedPrices():
    # This function is used for getting our locked in fuel prices to display on the main page

    # Remove all of our previous error messages
    session.pop('ErrorMessage', None)

    # Generate the tssa string
    tssa = generateTssa(BASE_URL + "FuelLock/List", "GET", None, session['accessToken'])

    # Assign the headers and then request the fuel prices.
    headers = {'User-Agent':'Apache-HttpClient/UNAVAILABLE (java 1.4)',
               'Authorization':'%s' % tssa,
               'X-OsVersion':OS_VERSION,
               'X-OsName':'Android',
               'X-DeviceID':session['DEVICE_ID'],
               'X-VmobID':des_encrypt_string(session['DEVICE_ID']),
               'X-AppVersion':APP_VERSION,
               'X-DeviceSecret':session['deviceSecret']}
               
    response = requests.get(BASE_URL + "FuelLock/List", headers=headers)
    returnContent = json.loads(response.content)

    # An error occours if we have never locked in a price before
    try:
        session['fuelLockId'] = returnContent[0]['Id']
        session['fuelLockStatus'] = returnContent[0]['Status']
        session['fuelLockActive'] = [0,0,0]
        session['fuelLockType'] = returnContent[0]['FuelGradeModel']
        session['fuelLockCPL'] = returnContent[0]['CentsPerLitre']
        session['fuelLockLitres'] = returnContent[0]['TotalLitres']

        tz = pytz.timezone(TZ)

        try:
            ts = returnContent[0]['RedeemedAt']
            session['fuelLockRedeemed'] = datetime.datetime.fromtimestamp(ts).astimezone(tz).strftime('%A %d %B %Y at %I:%M %p')
        except:
            session['fuelLockRedeemed'] = ""

        try:
            ts = returnContent[0]['ExpiresAt']
            session['fuelLockExpiry'] = datetime.datetime.fromtimestamp(ts).astimezone(tz).strftime('%A %d %B %Y at %I:%M %p')
        except:
            pass

        if(session['fuelLockStatus'] == 0):
            session['fuelLockActive'][0] = "Active"

        elif(session['fuelLockStatus'] == 1):
            session['fuelLockActive'][1] = "Expired"

        elif(session['fuelLockStatus'] == 2):
            session['fuelLockActive'][2] = "Redeemed"

        return session['fuelLockId'], session['fuelLockStatus'], session['fuelLockType'], session['fuelLockCPL'], session['fuelLockLitres'], session['fuelLockExpiry'], session['fuelLockRedeemed']

    except:
        # Since we haven't locked in a fuel price before
        session['fuelLockId'] = ""
        session['fuelLockStatus'] = ""
        session['fuelLockActive'] = ""
        session['fuelLockType'] = ""
        session['fuelLockCPL'] = ""
        session['fuelLockLitres'] = ""
        session['fuelLockRedeemed'] = ""
        session['fuelLockExpiry'] = ""

        return session['fuelLockId'], session['fuelLockStatus'], session['fuelLockType'], session['fuelLockCPL'], session['fuelLockLitres'], session['fuelLockExpiry'], session['fuelLockRedeemed']




def getStores():
    # Get a list of all of the stores and their features from the 7-Eleven server.
    # We will use this for our coordinates for a manual lock in
    tssa = generateTssa(BASE_URL + "store/StoresAfterDateTime/1001", "GET")
    deviceID = ''.join(random.choice('0123456789abcdef') for i in range(16))
    # Assign the headers
    headers = {'User-Agent':'Apache-HttpClient/UNAVAILABLE (java 1.4)',
               'Authorization':'%s' % tssa,
               'X-OsVersion':OS_VERSION,
               'X-OsName':'Android',
               'X-DeviceID':deviceID,
               'X-VmobID':des_encrypt_string(deviceID),
               'X-AppVersion':APP_VERSION}

    response = requests.get(BASE_URL + "store/StoresAfterDateTime/1001", headers=headers)
    return response.content

def getStoreAddress(storePostcode):
    # Open the stores.json file and read it as a JSON file
    with open('./stores.json', 'r') as f:
        stores = json.load(f)

    # For each store in "Diffs" read the postcode
    for store in stores['Diffs']:
        #print store['PostCode']
        if(store['PostCode'] == storePostcode):
            # Since we have a match, return the latitude + longitude of our store
            return str(store['Latitude']), str(store['Longitude'])

def des_encrypt_string(DEVICE_ID):
    # We only need the first 8 characters of the encryption key
    # Found in co.vmob.sdk.util.Utils.java
    key = 'co.vmob.sdk.android.encrypt.key'.encode()[:8]

    # The encryption prefix
    encryption_prefix = 'co.vmob.android.sdk.'
    # Now the encryption part
    cipher = pyDes.des(key, pyDes.ECB, pad=None, padmode=pyDes.PAD_PKCS5)
    encrypted_message = cipher.encrypt(encryption_prefix + DEVICE_ID)

    # Return the encrypted message base64 encoded and "decoded" so it is a string, not bytes.
    return base64.b64encode(encrypted_message).replace(b"/", b"_").decode() + "_"

# Encryption key used for the TSSA
encryption_key = bytes(base64.b64decode(getKey()))
if __name__ == '__main__':
    print("This should be run through app.py")
