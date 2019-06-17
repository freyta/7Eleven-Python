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

# Used to scrape ozbargain, and regex
from bs4 import BeautifulSoup, re
# Used for sending requests to 7-Eleven and getting the response in a JSON format
import requests, json
# Used to load details from the autolock.ini config file
import configparser
# Functions used for adding/subtracting from our coordinates and getting the time
import time, random
# Used for getting the variables and TSSA function etc
import functions

# A function to search the (new) deals page to see if there is a post about 7-Eleven fuel prices
def search_ozbargain():
    # We need to reiterate that suburb is global.. for some reason
    global suburb

    # Find 2 or 3 letters in the title surrounded by square brackets
    #regex_search = "(?=\[[A-Z]{2,3}\])"

    # The link to the deals page
    url = requests.get("https://www.ozbargain.com.au/deals").text
    # Open the deals page with BeautifulSoup
    soup = BeautifulSoup(url, "html.parser")

    # Find all deal posts with a title class
    response = soup.findAll('h2', class_="title")

    # Create a list to store all of the titles in case there is more than 1 current deal
    title = []

    for title_text in response:
        # If the words "7-Eleven" and "Fuel" is in the title, add it to our list
        # Adding "Fuel" should get rid of other deals posted
        if "7-Eleven" and "Fuel" in title_text.text:
            title.append(title_text.text)

    # Set suburb to none in case we don't find one later
    suburb = None

    # Search for the store location in the title of each deal
    for i in title:
        # Split after 7-Eleven to grab the store name (ignore text case)
        title_search = re.split("@ 7-Eleven", i, re.IGNORECASE)
        try:
            # Find a comma in
            suburb = re.sub("[^#@0-9A-Za-z ]+", "", title_search[1]).strip()
        except:
            suburb = title_search[1].strip()

    return suburb

# Search ProjectZeroThree.info too.
def search_pzt():
    # We need to reiterate that suburb is global.. for some reason
    global suburb
    # Load the ProjectZeroThree API into a JSON list
    url = requests.get("https://projectzerothree.info/api.php?format=json")
    # Find the cheapest price
    petrol_station = url.json()['regions'][0]['prices']
    # If the fuel type is U98 then get its suburb
    for i in petrol_station:
        if(i['type'] == "U98"):
            suburb = (i['suburb'])

    return suburb

def start_lockin():
    config = configparser.ConfigParser()
    config.read("./autolock.ini")
    # Get the setting if auto_lock is true or false
    auto_lock_enabled = config['General'].getboolean('auto_lock_enabled')
    # Get the maximum price we want to pay for fuel
    max_price = config['General']['max_price']
    # Check if we have saved a fuel lock
    fuel_lock_saved = config['Account'].getboolean('fuel_lock_saved')
    # Get the deviceSecret, this confirms we are locked in
    deviceSecret = config['Account']['deviceSecret']

    # If we have auto lock enabled, and are logged in but haven't saved a fuel lock yet, then proceed.
    if(auto_lock_enabled and deviceSecret and not fuel_lock_saved):
        # Get our account details
        deviceSecret = config['Account']['deviceSecret']
        accessToken = config['Account']['accessToken']
        cardBalance = config['Account']['cardBalance']
        DEVICE_ID = config['Account']['DEVICE_ID']

        # Search OzBargain for a new deal first, it may be posted there first
        if(not search_ozbargain()):
            # Search ProjectZeroThree since OzBargain has no results
            search_pzt()

        # If there is a location deal
        if(suburb):
            # Open the stores.json file so we can search it to find a store that (hopefully) matches
            with open('./stores.json', 'r') as f:
                stores = json.load(f)

            # For each store in "Diffs" read the postcode
            for store in stores['Diffs']:
                if(store['Suburb'] == suburb):
                    # Since we have a match, return the latitude + longitude of our store and add a random number to it.
                    latitude = store['Latitude']
                    latitude += (random.uniform(0.01,0.000001) * random.choice([-1,1]))
                    longitude = store['Longitude']
                    longitude += (random.uniform(0.01,0.000001) * random.choice([-1,1]))

            # The payload to start the lock in process.
            payload = '{"LastStoreUpdateTimestamp":' + str(int(time.time())) + ',"Latitude":"' + str(latitude) + '","Longitude":"' + str(longitude) + '"}'
            tssa = functions.generateTssa(functions.BASE_URL + "FuelLock/StartSession", "POST", payload, accessToken)

            # Now we start the request header
            headers = {'User-Agent':'Apache-HttpClient/UNAVAILABLE (java 1.4)',
                       'Authorization':'%s' % tssa,
                       'X-OsVersion':functions.OS_VERSION,
                       'X-OsName':'Android',
                       'X-DeviceID':DEVICE_ID,
                       'X-AppVersion':functions.APP_VERSION,
                       'X-DeviceSecret':deviceSecret,
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
                  # Print that we have a lock in already
                  print("Tried to lock in, but we already have a lock in saved.")
            except:
                # Get the fuel price of all the types of fuel
                for each in returnContent['CheapestFuelTypeStores']:
                    x = each['FuelPrices']
                    for i in x:
                        # If the fuel type is premium 98
                        if(i['Ean'] == 56):
                            # Save the fuel pump price
                            pump_price = i['Price']

                # If the price that we tried to lock in is more expensive than scripts price, we return an error
                if (float(pump_price) >= float(max_price)):
                    print("There was a new deal posted, but the fuel price was too expensive. You want to fill up for less than {0}c, i t would have been {1}c.".format(str(max_price), str(pump_price)))
                else:
                    # Now we want to lock in the maximum litres we can.
                    NumberOfLitres = int(float(config['Account']['cardbalance']) / pump_price * 100)

                    # Lets start the actual lock in process
                    payload = '{"AccountId":"' + config['Account']['account_id'] + '","FuelType":"56","NumberOfLitres":"' + str(NumberOfLitres) + '"}'

                    tssa = functions.generateTssa(functions.BASE_URL + "FuelLock/Confirm", "POST", payload, accessToken)

                    headers = {'User-Agent':'Apache-HttpClient/UNAVAILABLE (java 1.4)',
                               'Authorization':'%s' % tssa,
                               'X-OsVersion':functions.OS_VERSION,
                               'X-OsName':'Android',
                               'X-DeviceID':DEVICE_ID,
                               'X-AppVersion':functions.APP_VERSION,
                               'X-DeviceSecret':deviceSecret,
                               'Content-Type':'application/json; charset=utf-8'}

                    # Send through the request and get the response
                    response = requests.post(functions.BASE_URL + "FuelLock/Confirm", data=payload, headers=headers)
                    returnContent = json.loads(response.content)

                    try:
                        if(returnContent['Message']):
                            print("Error: There was an error locking in.")
                    except:
                            print("Success! Locked in {0}L at {1} cents per litre".format(str(returnContent['TotalLitres']), str(returnContent['CentsPerLitre'])))
if __name__ == '__main__':
    # Make the variable suburb global
    global suburb
    suburb = None
    print("This should be run through app.py")
