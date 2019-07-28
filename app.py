#-*- coding: utf8 -*-
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


from flask import Flask, render_template, request, redirect, url_for, session, flash

# Optional Security
# Uncomment Basic Auth section to enable basic authentication so users will be prompted a username and password before seeing the website.
#from flask_basicauth import BasicAuth

# Uncomment SSL section to enable HTTPS (certificates required)
#import ssl
#context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
#context.load_cert_chain('domain.crt', 'domain.key')

# Used for getting/settings the OS environments and for writing/reading the stores.json file
import sys, os, time
# Used for sending requests to 7-Eleven and getting the response in a JSON format.
import requests, json
# Used for our randomly generated Device ID (if needed)
import random
# Used to set our coordinates while locking in a price
import googlemaps
# Used for all of our custom settings and functions
import settings, functions
# Used for the auto locking function
from apscheduler.schedulers.background import BackgroundScheduler
# Used to load and save details from the autolock.ini config file and import our autolocker
import autolocker, configparser


# If we haven't set the API key or it is it's default value, warn the user that we will disable the Google Maps search.
if(functions.API_KEY in [None,"changethis",""]):
    custom_coords = False
    print("Note: You have not set an API key. You will not be able to use Google to find a stores coordinates.\nBut you can still use the manual search if you know the postcode to the store you want to lock in from.\n\n\n\n\n")

# If we have not set a device ID then let them know a random one will be generated
if(os.getenv('DEVICE_ID', settings.DEVICE_ID) in [None,"changethis",""]):
    print("Note: You have not set a device ID. A random one will be set when you login.")



app = Flask(__name__)

# Uncomment to enable basic authentication
#app.config['BASIC_AUTH_FORCE'] = True
#app.config['BASIC_AUTH_USERNAME'] = 'petrol'
#app.config['BASIC_AUTH_PASSWORD'] = 'lockit'
#basic_auth = BasicAuth(app)

@app.route('/')
def index():

    # If they have pressed the refresh link remove the error and success messages
    if(request.args.get('action') == "refresh"):
        session.pop('ErrorMessage', None)
        session.pop('SuccessMessage', None)
        session.pop('fuelType', None)
        session.pop('LockinPrice', None)
        try:
            # Regenerate our locked in prices
            functions.lockedPrices()
        except:
            # If there was an error, lets just move on.
            pass

    # If the environmental variable DEVICE_ID is empty or is not set at all
    if(os.getenv('DEVICE_ID', settings.DEVICE_ID) in [None,"changethis",""]):
        # Set the device id to a randomly generated one
        DEVICE_ID = ''.join(random.choice('0123456789abcdef') for i in range(16))
    else:
        # Otherwise we set the it to the one set in settings.py
        DEVICE_ID = os.getenv('DEVICE_ID', settings.DEVICE_ID)

    # Set the session max price for the auto locker
    session['max_price'] = config['General']['max_price']

    # Get the cheapest fuel price to show on the automatic lock in page
    fuelPrice = functions.cheapestFuelAll()

    return render_template('price.html',device_id=DEVICE_ID)



@app.route('/login', methods=['POST', 'GET'])
def login():
    # Clear the error and success message
    session.pop('ErrorMessage', None)
    session.pop('SuccessMessage', None)
    session.pop('fuelType', None)

    if request.method == 'POST':
        # If the device ID field was left blank, set a random one
        if ((request.form['device_id']) in [None,""]):
            session['DEVICE_ID'] = os.getenv('DEVICE_ID', ''.join(random.choice('0123456789abcdef') for i in range(16)))
        else:
            # Since it was filled out, we will use that for the rest of the session
            session['DEVICE_ID'] = os.getenv('DEVICE_ID', request.form['device_id'])

        # Get the email and password from the login form
        password = str(request.form['password'])
        email = str(request.form['email'])

        # The payload that we use to login
        payload = '{"Email":"' + email + '","Password":"' + password + '","DeviceName":"' + functions.DEVICE_NAME + '","DeviceOsNameVersion":"' + functions.OS_VERSION +'"}'

        # Generate the tssa string
        tssa = functions.generateTssa(functions.BASE_URL + "account/login", "POST", payload)

        # Assign the headers
        headers = {'User-Agent':'Apache-HttpClient/UNAVAILABLE (java 1.4)',
                   'Authorization':'%s' % tssa,
                   'X-OsVersion':functions.OS_VERSION,
                   'X-OsName':'Android',
                   'X-DeviceID':session['DEVICE_ID'],
                   'X-VmobID':functions.des_encrypt_string(session['DEVICE_ID']),
                   'X-AppVersion':functions.APP_VERSION,
                   'Content-Type':'application/json; charset=utf-8'}

        # Login now!
        response = requests.post(functions.BASE_URL + "account/login", data=payload, headers=headers)

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


            functions.lockedPrices()


            # If we have ticked enable auto lock in, then set boolean to true
            if(request.form.getlist('auto_lockin')):
                config.set('General', 'auto_lock_enabled', "True")
                session['auto_lock'] = True
            else:
                # We didn't want to save it, so set to false
                config.set('General', 'auto_lock_enabled', "False")
                session['auto_lock'] = False

            # Save their log in anyway, so we can update the auto lock option later if needed
            config.set('Account', 'deviceSecret', session['deviceSecret'])
            config.set('Account', 'accessToken', session['accessToken'])
            config.set('Account', 'cardBalance', session['cardBalance'])
            config.set('Account', 'account_ID', session['accountID'])
            config.set('Account', 'DEVICE_ID', session['DEVICE_ID'])

            # If we have an active fuel lock, set fuel_lock_saved to true, otherwise false
            if(session['fuelLockStatus'] == 0):
                config.set('Account', 'fuel_lock_saved', "True")
            else:
                config.set('Account', 'fuel_lock_saved', "False")
            # Write the config to file
            with open('./autolock.ini', 'w') as configfile:
                config.write(configfile)

            return redirect(url_for('index'))
    else:
        # They didn't submit a POST request, so we will redirect to index
        return redirect(url_for('index'))


@app.route('/logout')
def logout():

    # The logout payload is an empty string but it is still needed
    payload = '""'
    tssa = functions.generateTssa(functions.BASE_URL + "account/logout", "POST", payload, session['accessToken'])

    headers = {'User-Agent':'Apache-HttpClient/UNAVAILABLE (java 1.4)',
               'Authorization':'%s' % tssa,
               'X-OsVersion':functions.OS_VERSION,
               'X-OsName':'Android',
               'X-DeviceID':session['DEVICE_ID'],
               'X-VmobID':functions.des_encrypt_string(session['DEVICE_ID']),
               'X-AppVersion':functions.APP_VERSION,
               'X-DeviceSecret':session['deviceSecret'],
               'Content-Type':'application/json; charset=utf-8'}

    response = requests.post(functions.BASE_URL + "account/logout", data=payload, headers=headers)

    # Clear all of the previously set session variables and then redirect to the index page
    session.clear()

    return redirect(url_for('index'))

# The confirmation page for a manual lock in
@app.route('/confirm')
def confirm():
    # See if we have a temporary lock in price
    try:
        if(session['LockinPrice']):
            # Since we do, show the confirmation page
            return render_template('confirm_price.html')
    except:
        # We haven't started locking in yet, show an error and redirect to the index
        session['ErrorMessage'] = "You haven't started the lock in process yet. Please try again."
        return redirect(url_for('index'))


# Save the auto lock in settings
@app.route('/save_settings',  methods=['POST'])
def save_settings():
    # If we have sent the form
    if request.method == 'POST':
        # If we want to auto lock in, set it to true
        if(request.form.getlist('auto_lockin')):
            config.set('General', 'auto_lock_enabled', "True")
            session['auto_lock'] = True
        else:
            config.set('General', 'auto_lock_enabled', "False")
            session['auto_lock'] = False

        # Set the max price to what the user wants as long as it's above 1 dollar and below 2 dollars
        # Note: Minimum price is $1 to try and avoid any 'honeypot stings' where premium unleaded
        # is obviously too cheap for us to lock in.
        if (float(request.form['max_price']) > 100 and float(request.form['max_price']) < 200):
            config.set('General', 'max_price', request.form['max_price'])
        else:
            session['ErrorMessage'] = "The price you tried to lock in was either too cheap or too expensive. It should be between 100 and 200cents"
            return redirect(url_for('index'))
        # Save the config file
        with open('./autolock.ini', 'w') as configfile:
            config.write(configfile)

        session['SuccessMessage'] = "Settings saved succesfully."
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
            locationResult = functions.cheapestFuel(fuelType)

            # They tried to do something different from the manual and automatic form, so throw up an error
            if(submissionMethod != "manual" and submissionMethod != "automatic"):
                session['ErrorMessage'] = "Invalid form submission. Either use the manual or automatic one on the main page."
                return redirect(url_for('index'))

            # If they have manually chosen a postcode/suburb set the price overide to true
            if(submissionMethod == "manual"):
                postcode = str(request.form['postcode'])
                priceOveride = True
                # Get the latitude and longitude from the store
                storeLatLng = functions.getStoreAddress(postcode)
                # If we have a match, set the coordinates. If we don't, use Google Maps
                if (storeLatLng):
                    locLat = float(storeLatLng[0])
                    locLat += (random.uniform(0.01,0.000001) * random.choice([-1,1]))

                    locLong = float(storeLatLng[1])
                    locLong += (random.uniform(0.01,0.000001) * random.choice([-1,1]))
                else:
                    # If we have entered the wrong manual postcode for a store, and haven't
                    # set the Google Maps API, return an error since we cant use the API
                    if not custom_coords:
                        # If it is, get the error message and return back to the index
                        session['ErrorMessage'] = "Error: You entered a manual postcode where no 7-Eleven store is. Please set a Google Maps API key or enter a valid postcode."
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
            tssa = functions.generateTssa(functions.BASE_URL + "FuelLock/StartSession", "POST", payload, session['accessToken'])

            # Now we start the request header
            headers = {'User-Agent':'Apache-HttpClient/UNAVAILABLE (java 1.4)',
                       'Authorization':'%s' % tssa,
                       'X-OsVersion':functions.OS_VERSION,
                       'X-OsName':'Android',
                       'X-DeviceID':session['DEVICE_ID'],
                       'X-VmobID':functions.des_encrypt_string(session['DEVICE_ID']),
                       'X-AppVersion':functions.APP_VERSION,
                       'X-DeviceSecret':session['deviceSecret'],
                       'Content-Type':'application/json; charset=utf-8'}

            # Send the request
            response = requests.post(functions.BASE_URL + "FuelLock/StartSession", data=payload, headers=headers)

            # Get the response content so we can check the fuel price
            returnContent = response.content

            # Move the response json into an array so we can read it
            returnContent = json.loads(returnContent)

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

        tssa = functions.generateTssa(functions.BASE_URL + "FuelLock/Confirm", "POST", payload, session['accessToken'])

        headers = {'User-Agent':'Apache-HttpClient/UNAVAILABLE (java 1.4)',
                   'Authorization':'%s' % tssa,
                   'X-OsVersion':functions.OS_VERSION,
                   'X-OsName':'Android',
                   'X-DeviceID':session['DEVICE_ID'],
                   'X-VmobID':functions.des_encrypt_string(session['DEVICE_ID']),
                   'X-AppVersion':functions.APP_VERSION,
                   'X-DeviceSecret':session['deviceSecret'],
                   'Content-Type':'application/json; charset=utf-8'}

        # Send through the request and get the response
        response = requests.post(functions.BASE_URL + "FuelLock/Confirm", data=payload, headers=headers)

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
                functions.lockedPrices()
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
            functions.lockedPrices()
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
                print("Note: Opening stores.json")
                stores = json.load(f)
            except:
                pass
        try:
            # Check to see if the stores.json file is older than 1 week.
            # If it is, we will download a new version
            if(stores['AsOfDate'] < (time.time() - (60 * 60 * 24 * 7))):
                print("Note: Your stores.json file is too old, updating it..")
                with open('./stores.json', 'wb') as f:
                    f.write(functions.getStores())

                print("Note: Updating stores.json complete")
        except:
            # Our json file isn't what we expected, so we will download a new one.
            with open('./stores.json', 'wb') as f:
                f.write(functions.getStores())

    else:
        # We have no stores.json file, so we wil download it
        print("Note: No stores.json found, creating it for you.")
        with open('./stores.json', 'wb') as f:
            f.write(functions.getStores())

    # Open the config file and read the settings
    config = configparser.ConfigParser()
    config.read("./autolock.ini")

    # Start the autosearch scheduler
    if(functions.TZ in [None,""]):
        scheduler = BackgroundScheduler(timezone='UTC')
    else:
        scheduler = BackgroundScheduler(timezone=functions.TZ)
    # Start the price search thread and run it every 30 minutes
    scheduler.add_job(autolocker.start_lockin, 'interval', seconds=1800)
    scheduler.start()

    app.secret_key = os.urandom(12)
    app.run(host='0.0.0.0')

    # Uncomment to enable HTTPS/SSL and comment out the line above
    #app.run(host='0.0.0.0',port=443,ssl_context=context)
