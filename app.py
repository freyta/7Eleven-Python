#-*- coding: utf8 -*-

#    7-Eleven Python implementation. This program allows you to lock in a fuel price from your computer.
#    Copyright (C) 2018  Freyta
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


from flask import Flask, render_template, request, redirect, url_for, session, flash

import sys
import os
import pytz
import hashlib
import hmac
import base64
import time
import uuid
import requests
import json
import random
import datetime
import googlemaps
import settings

'''''''''''''''''''''''''''
Set API_KEY in the settings.py file
'''''''''''''''''''''''''''
API_KEY = os.getenv('API_KEY',settings.API_KEY)
TZ = os.getenv('TZ', settings.TZ)
BASE_URL = os.getenv('BASE_URL',settings.BASE_URL)
PRICE_URL = os.getenv('PRICE_URL',settings.PRICE_URL)
DEVICE_NAME = os.getenv('DEVICE_NAME', settings.DEVICE_NAME)
OS_VERSION = os.getenv('OS_VERSION', settings.OS_VERSION)
APP_VERSION = os.getenv('APP_VERSION', settings.APP_VERSION)
DEVICE_ID = os.getenv('DEVICE_ID', settings.DEVICE_ID)

# If we haven't set the API key or it is it's default value, warn the user that we will disable the Google Maps search.
if(API_KEY in [None,"changethis",""]):
    custom_coords = False
    print("Note: You have not set an API key. You will not be able to use Google to find a stores coordinates.\nBut you can still use the manual search if you know the postcode to the store you want to lock in from.\n\n\n\n\n")

if(DEVICE_ID in [None,"changethis",""]):
    DEVICE_ID = ''.join(random.choice('0123456789abcdef') for i in range(15))
    print("Note: You have not set a device ID. Randomly generating one: " + DEVICE_ID)

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
               'X-DeviceID':DEVICE_ID,
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
    deviceID = ''.join(random.choice('0123456789abcdef') for i in range(15))
    # Assign the headers
    headers = {'User-Agent':'Apache-HttpClient/UNAVAILABLE (java 1.4)',
               'Authorization':'%s' % tssa,
               'X-OsVersion':OS_VERSION,
               'X-OsName':'Android',
               'X-DeviceID':deviceID,
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

def getKey():

    a = [103, 180, 267, 204, 390, 504, 497, 784, 1035, 520, 1155, 648, 988, 1456, 1785]
    b = [50, 114, 327, 276, 525, 522, 371, 904, 1017, 810, 858, 852, 1274, 1148, 915]
    c = [74, 220, 249, 416, 430, 726, 840, 568, 1017, 700, 1155, 912, 1118, 1372]

    length = len(a) + len(b) + len(c)
    key = ""

    for i in range(length):
        if(i % 3 == 0):
            key += chr( int((a[int(i / 3)] / ((i / 3) + 1)) ))
        if(i % 3 == 1):
            key += chr( int((b[int((i - 1) / 3)] / (((i - 1) / 3) + 1)) ))
        if(i % 3 == 2):
            key += chr( int((c[int((i - 1) / 3)] / (((i - 2) / 3) + 1)) ))
    return key

# Generate the tssa string
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
        print (str3)
    signature = base64.b64encode(hmac.new(encryption_key, str3.encode(), digestmod=hashlib.sha256).digest())

    # Finish building the tssa string
    tssa = "tssa yvktroj08t9jltr3ze0isf7r4wygb39s:" + signature.decode() + ":" + uuidVar + ":" + str(timestamp)
    # If we have an access token append it to the tssa string
    if(accessToken):
        tssa += ":" + accessToken

    return tssa

# Encryption key used for the TSSA
encryption_key = bytes(base64.b64decode(getKey()))
# The current time
timeNow = int(time.time())

app = Flask(__name__)
@app.route('/')
def index():
    # If they have pressed the refresh link remove the error and success messages
    if(request.args.get('action') == "refresh"):
        session.pop('ErrorMessage', None)
        session.pop('SuccessMessage', None)
        session.pop('fuelType', None)
        session.pop('LockinPrice', None)
        try:
            lockedPrices()
        except:
            pass

    # Get the cheapest fuel price to show on the automatic lock in page
    fuelPrice = cheapestFuelAll()
    return render_template('price.html')



@app.route('/login', methods=['POST', 'GET'])
def login():
    # Clear the error and success message
    session.pop('ErrorMessage', None)
    session.pop('SuccessMessage', None)
    session.pop('fuelType', None)

    if request.method == 'POST':
        password = str(request.form['password'])
        email = str(request.form['email'])

        # The payload that we use to login
        payload = '{"Email":"' + email + '","Password":"' + password + '","DeviceName":"' + DEVICE_NAME + '","DeviceOsNameVersion":"' + OS_VERSION +'"}'

        # Generate the tssa string
        tssa = generateTssa(BASE_URL + "account/login", "POST", payload)

        # Assign the headers
        headers = {'User-Agent':'Apache-HttpClient/UNAVAILABLE (java 1.4)',
                   'Authorization':'%s' % tssa,
                   'X-OsVersion':OS_VERSION,
                   'X-OsName':'Android',
                   'X-DeviceID':DEVICE_ID,
                   'X-AppVersion':APP_VERSION,
                   'Content-Type':'application/json; charset=utf-8'}

        # Login now!
        response = requests.post(BASE_URL + "account/login", data=payload, headers=headers)

        returnHeaders = response.headers
        returnContent = json.loads(response.text)

        try:
            # If there was an error logging in, redirect to the index page with the 7Eleven response
            if(returnContent['Message']):
                session['ErrorMessage'] = returnContent['Message']
                return redirect(url_for('index'))

        except:

            # We need the AccessToken from the response header
            accessToken = str(returnHeaders).split("'X-AccessToken': '")
            accessToken = accessToken[1].split("'")
            accessToken = accessToken[0]

            # DeviceSecretToken and accountID are both needed to lock in a fuel price
            deviceSecret = returnContent['DeviceSecretToken']
            accountID    = returnContent['AccountId']
            # Save the users first name and their card balance so we can display it
            firstName    = returnContent['FirstName']
            cardBalance  = str(returnContent['DigitalCard']['Balance'])

            session['deviceSecret'] = deviceSecret
            session['accessToken'] = accessToken
            session['accountID'] = accountID
            session['firstName'] = firstName
            session['cardBalance'] = cardBalance

            lockedPrices()
            return redirect(url_for('index'))
    else:
        # They didn't submit a POST request, so we will redirect to index
        return redirect(url_for('index'))


@app.route('/logout')
def logout():

    # The logout payload is an empty string but it is still needed
    payload = '""'
    tssa = generateTssa(BASE_URL + "account/logout", "POST", payload, session['accessToken'])

    headers = {'User-Agent':'Apache-HttpClient/UNAVAILABLE (java 1.4)',
               'Authorization':'%s' % tssa,
               'X-OsVersion':OS_VERSION,
               'X-OsName':'Android',
               'X-DeviceID':DEVICE_ID,
               'X-AppVersion':APP_VERSION,
               'X-DeviceSecret':session['deviceSecret'],
               'Content-Type':'application/json; charset=utf-8'}

    response = requests.post(BASE_URL + "account/logout", data=payload, headers=headers)
    # Clear all of the previously set session variables and then redirect to the index page
    session.clear()
    return redirect(url_for('index'))

@app.route('/confirm')
def confirm():

    try:
        if(session['LockinPrice']):
            return render_template('confirm_price.html')
    except:
        session['ErrorMessage'] = "You haven't started the lock in process yet. Please try again."
        return redirect(url_for('index'))




@app.route('/lockin',  methods=['POST', 'GET'])
def lockin():
    if request.method == 'POST':
        # Variable used to search for a manual price
        priceOveride = False
        # Get the form submission method
        submissionMethod = request.form['submit']

        # If we didn't try to confirm a manual price
        if(submissionMethod != "confirm_price"):

            # Get the fuel type we want
            fuelType = str(request.form['fueltype'])
            session['fuelType'] = fuelType

            # Clear previous messages
            session.pop('ErrorMessage', None)
            session.pop('SuccessMessage', None)

            # Get the postcode and price of the cheapest fuel
            locationResult = cheapestFuel(fuelType)

            # They tried to do something different from the manual and automatic form, so throw up an error
            if(submissionMethod != "manual" and submissionMethod != "automatic"):
                session['ErrorMessage'] = "Invalid form submission. Either use the manual or automatic one on the main page."
                return redirect(url_for('index'))

            # If they have manually chosen a postcode/suburb set the price overide to true
            if(submissionMethod == "manual"):
                postcode = str(request.form['postcode'])
                priceOveride = True
                # Get the latitude and longitude from the store
                storeLatLng = getStoreAddress(postcode)
                # If we have a match, set the coordinates. If we don't, use Google Maps
                if (storeLatLng):
                    locLat = float(storeLatLng[0])
                    locLat += (random.uniform(0.01,0.000001) * random.choice([-1,1]))

                    locLong = float(storeLatLng[1])
                    locLong += (random.uniform(0.01,0.000001) * random.choice([-1,1]))
                else:
                    # If we have made entered the wrong manual postcode for a store, and haven't
                    # set the Google Maps API, return an error since we cant use the API
                    if not custom_coords:
                        # If it is, get the error message and return back to the index
                        session['ErrorMessage'] = "Error: You entered a manual postcode where no 7Eleven store is. Please set a Google Maps API key or enter a valid postcode."
                        return redirect(url_for('index'))
                    # Initiate the Google Maps API
                    gmaps = googlemaps.Client(key = API_KEY)
                    # Get the longitude and latitude from the submitted postcode
                    geocode_result = gmaps.geocode(str(request.form['postcode']) + ', Australia')
                    locLat  = geocode_result[0]['geometry']['location']['lat']
                    locLong = geocode_result[0]['geometry']['location']['lng']
            else:
                # It was an automatic submission so we will now get the coordinates of the store
                # and add a random value to it so we don't appear to lock in from the service station
                locLat = locationResult[2]
                locLat += (random.uniform(0.01,0.000001) * random.choice([-1,1]))

                locLong = locationResult[3]
                locLong += (random.uniform(0.01,0.000001) * random.choice([-1,1]))

            # The payload to start the lock in process.
            payload = '{"LastStoreUpdateTimestamp":' + str(int(time.time())) + ',"Latitude":"' + str(locLat) + '","Longitude":"' + str(locLong) + '"}'
            tssa = generateTssa(BASE_URL + "FuelLock/StartSession", "POST", payload, session['accessToken'])

            # Now we start the request header
            headers = {'User-Agent':'Apache-HttpClient/UNAVAILABLE (java 1.4)',
                       'Authorization':'%s' % tssa,
                       'X-OsVersion':OS_VERSION,
                       'X-OsName':'Android',
                       'X-DeviceID':DEVICE_ID,
                       'X-AppVersion':APP_VERSION,
                       'X-DeviceSecret':session['deviceSecret'],
                       'Content-Type':'application/json; charset=utf-8'}

            # Send the request
            response = requests.post(BASE_URL + "FuelLock/StartSession", data=payload, headers=headers)

            # Get the response content so we can check the fuel price
            returnContent = response.content

            # Move the response json into an array so we can read it
            returnContent = json.loads(returnContent)
            # Get the store number - I don't think we need this, so I have commented it out!
            #storeNumber = returnContent['CheapestFuelTypeStores'][0]['StoreNumber']

            # If there is a fuel lock already in place we get an error!
            try:
              if returnContent['ErrorType'] == 0:
                  session['ErrorMessage'] = "An error has occured. This is most likely due to a fuel lock already being in place."
                  return redirect(url_for('index'))
            except:
                pass

            # Get the fuel price of all the types of fuel
            for each in returnContent['CheapestFuelTypeStores']:
                x = each['FuelPrices']
                for i in x:
                    if(str(i['Ean']) == fuelType):
                        LockinPrice = i['Price']
                        session['LockinPrice'] = LockinPrice

            # If we have performed an automatic search we run the lowest price check
            # LockinPrice = the price from the 7/11 website
            # locationResult[1] = the price from the master131 script
            # If the price that we tried to lock in is more expensive than scripts price, we return an error
            if not(priceOveride):
                if not(float(LockinPrice) <= float(locationResult[1])):
                    session['ErrorMessage'] = "The fuel price is too high compared to the cheapest available. The cheapest we found was at " + locationResult[0] + ". Try locking in there!"
                    return redirect(url_for('index'))

            if(priceOveride):
                return redirect(url_for('confirm'))

        # Now we want to lock in the maximum litres we can.
        NumberOfLitres = int(float(session['cardBalance']) / session['LockinPrice'] * 100)

        # Lets start the actual lock in process
        payload = '{"AccountId":"' + session['accountID'] + '","FuelType":"' + session['fuelType'] + '","NumberOfLitres":"' + str(NumberOfLitres) + '"}'

        tssa = generateTssa(BASE_URL + "FuelLock/Confirm", "POST", payload, session['accessToken'])

        headers = {'User-Agent':'Apache-HttpClient/UNAVAILABLE (java 1.4)',
                   'Authorization':'%s' % tssa,
                   'X-OsVersion':OS_VERSION,
                   'X-OsName':'Android',
                   'X-DeviceID':DEVICE_ID,
                   'X-AppVersion':APP_VERSION,
                   'X-DeviceSecret':session['deviceSecret'],
                   'Content-Type':'application/json; charset=utf-8'}

        # Send through the request and get the response
        response = requests.post(BASE_URL + "FuelLock/Confirm", data=payload, headers=headers)

        # Get the response into a json array
        returnContent = json.loads(response.content)
        try:
            # Check if the response was an error message
            if(returnContent['Message']):
                # If it is, get the error message and return back to the index
                session['ErrorMessage'] = returnContent['Message']
                return redirect(url_for('index'))
            # Otherwise we most likely locked in the price!
            if(returnContent['Status'] == "0"):
                # Update the fuel prices that are locked in
                lockedPrices()
                # Get amoount of litres that was locked in from the returned JSON array
                session['TotalLitres'] = returnContent['TotalLitres']
                session['SuccessMessage'] = "The price was locked in for " + str(session['LockinPrice']) + " cents per litre"

                # Pop our fueltype and lock in price variables
                session.pop('fuelType', None)
                session.pop('LockinPrice', None)
                return redirect(url_for('index'))

        # For whatever reason it saved our lock in anyway and return to the index page
        except:
            # Update the fuel prices that are locked in
            lockedPrices()
            session['SuccessMessage'] = "The price was locked in for " + str(session['LockinPrice']) + " cents per litre"
            # Get amoount of litres that was locked in from the returned JSON array
            session['TotalLitres'] = returnContent['TotalLitres']

            # Pop our fueltype and lock in price variables
            session.pop('fuelType', None)
            session.pop('LockinPrice', None)
            return redirect(url_for('index'))
    else:
        # They just tried to load the lock in page without sending any data
        session['ErrorMessage'] = "Unknown error occured. Please try again!"
        return redirect(url_for('index'))

if __name__ == '__main__':
    # Try and open stores.json
    if(os.path.isfile('./stores.json')):
        with open('./stores.json', 'r') as f:
            try:
                stores = json.load(f)
            except:
                pass
        try:
            # Check to see if the stores.json file is older than 1 week.
            # If it is, we will download a new version
            if(stores['AsOfDate'] < (time.time() - (60 * 60 * 24 * 7))):
                with open('./stores.json', 'wb') as f:
                    f.write(getStores())
        except:
            # Our json file isn't what we expected, so we will download a new one.
            with open('./stores.json', 'wb') as f:
                f.write(getStores())

    else:
        # We have no stores.json file, so we wil download it
        with open('./stores.json', 'wb') as f:
            f.write(getStores())

    app.secret_key = os.urandom(12)
    app.run(host='0.0.0.0')
