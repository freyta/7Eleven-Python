'''
    7-Eleven Python implementation.

    Copyright (C) 2019  Freyta
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with this program. If not, see <https://www.gnu.org/licenses/>.
'''

from . import *

def listFuellock(deviceSecret, accessToken):

    tssa = generateTssa(BASE_URL + "FuelLock/List", "GET", "", accessToken)

    headers = {'User-Agent':'Apache-HttpClient/UNAVAILABLE (java 1.4)',
               'Connection':'Keep-Alive',
               'Host':'711-goodcall.api.tigerspike.com',
               'Authorization':'%s' % tssa,
               'X-OsVersion':ANDROID_VERSION,
               'X-OsName':'Android',
               'X-DeviceID':DEVICE_ID,
               'X-AppVersion':APP_VERSION,
               'X-DeviceSecret':deviceSecret}

    response = requests.get(BASE_URL + "FuelLock/List", headers=headers)

    return(response.content)

def startLockinSession(deviceSecret, accessToken, locLat, locLong):

    current_time = str(int(time.time()))
    payload = f'{{"LastStoreUpdateTimestamp":{current_time},"Latitude":"{locLat}","Longitude":"{locLong}"}}'

    tssa = generateTssa(BASE_URL + "FuelLock/StartSession", "POST", payload, accessToken)

    headers = {'User-Agent':'Apache-HttpClient/UNAVAILABLE (java 1.4)',
               'Connection':'Keep-Alive',
               'Host':'711-goodcall.api.tigerspike.com',
               'Authorization':'%s' % tssa,
               'X-OsVersion':ANDROID_VERSION,
               'X-OsName':'Android',
               'X-DeviceID':DEVICE_ID,
               'X-AppVersion':APP_VERSION,
               'X-DeviceSecret':deviceSecret,
               'Content-Type':'application/json; charset=utf-8'}

    response = requests.post(BASE_URL + "FuelLock/StartSession", data=payload, headers=headers)

    return(response.content)


def confirmLockin(deviceSecret, accessToken, accountID, fuel_type, litres):

    '''
    FUEL TYPE OPTIONS
    52 = Unleaded 91
    53 = Diesel
    54 = LPG
    55 = Unleaded 95
    56 = Unleaded 98
    57 = E10
    '''

    payload = '{"AccountId":"' + accountID + '","FuelType":' + fuel_type + ',"NumberOfLitres":' + litres + '}'
    tssa = generateTssa(BASE_URL + "FuelLock/Confirm", "POST", payload, accessToken)

    headers = {'User-Agent':'Apache-HttpClient/UNAVAILABLE (java 1.4)',
               'Connection':'Keep-Alive',
               'Host':'711-goodcall.api.tigerspike.com',
               'Authorization':'%s' % tssa,
               'X-OsVersion':ANDROID_VERSION,
               'X-OsName':'Android',
               'X-DeviceID':DEVICE_ID,
               'X-AppVersion':APP_VERSION,
               'X-DeviceSecret':deviceSecret,
               'Content-Type':'application/json; charset=utf-8'}

    response = requests.post(BASE_URL + "FuelLock/Confirm", data=payload, headers=headers)

    return(response.content)


# Below doesn't work, but it is in the app source code. Maybe it used to work at some stage?
def redeemLockin(deviceSecret, accessToken, id):

    tssa = generateTssa(BASE_URL + "FuelLock/Redeem?fuelLockId=" + id, "GET", "")

    headers = {'User-Agent':'Apache-HttpClient/UNAVAILABLE (java 1.4)',
               'Connection':'Keep-Alive',
               'Host':'711-goodcall.api.tigerspike.com',
               'Authorization':'%s' % tssa,
               'X-OsVersion':ANDROID_VERSION,
               'X-OsName':'Android',
               'X-DeviceID':DEVICE_ID,
               'X-AppVersion':APP_VERSION,
               'X-DeviceSecret':deviceSecret}

    response = requests.get(BASE_URL + "FuelLock/Redeem?fuelLockId=" + id, headers=headers)

    return(response.content)

def isFplRedeemed(deviceSecret, accessToken, id):

    tssa = generateTssa(BASE_URL + "FuelLock/IsRedeemed?fuelLockId=" + id, "GET", "", accessToken)
    headers = {'User-Agent':'Apache-HttpClient/UNAVAILABLE (java 1.4)',
               'Connection':'Keep-Alive',
               'Host':'711-goodcall.api.tigerspike.com',
               'Authorization':'%s' % tssa,
               'X-OsVersion':ANDROID_VERSION,
               'X-OsName':'Android',
               'X-DeviceID':DEVICE_ID,
               'X-AppVersion':APP_VERSION,
               'X-DeviceSecret':deviceSecret}

    response = requests.get(BASE_URL + "FuelLock/IsRedeemed?fuelLockId=" + id, headers=headers)

    # If response is empty, then fuel lock has been redeemed
    return(response.content)


def refreshFplData(deviceSecret, accessToken, id):

    tssa = generateTssa(BASE_URL + "FuelLock/Refresh?fuelLockId=" + id, "GET", "", accessToken)

    headers = {'User-Agent':'Apache-HttpClient/UNAVAILABLE (java 1.4)',
               'Connection':'Keep-Alive',
               'Host':'711-goodcall.api.tigerspike.com',
               'Authorization':'%s' % tssa,
               'X-OsVersion':ANDROID_VERSION,
               'X-OsName':'Android',
               'X-DeviceID':DEVICE_ID,
               'X-AppVersion':APP_VERSION,
               'X-DeviceSecret':deviceSecret}

    response = requests.get(BASE_URL + "FuelLock/Refresh?fuelLockId=" + id, headers=headers)

    # If response is empty, then fuel lock has been redeemed
    return(response.content)


def checkFuelPrice(store):

    tssa = generateTssa(BASE_URL + "FuelPrice/FuelPriceForStore/" + store, "GET", "")

    headers = {'User-Agent':'Apache-HttpClient/UNAVAILABLE (java 1.4)',
               'Connection':'Keep-Alive',
               'Host':'711-goodcall.api.tigerspike.com',
               'Authorization':'%s' % tssa,
               'X-OsVersion':ANDROID_VERSION,
               'X-OsName':'Android',
               'X-DeviceID':DEVICE_ID,
               'X-AppVersion':APP_VERSION}

    response = requests.get(BASE_URL + "FuelPrice/FuelPriceForStore/" + store, headers=headers)

    return(response.content)

def getStores():

    tssa = generateTssa(BASE_URL + "store/StoresAfterDateTime/1001", "GET", "")

    headers = {'User-Agent':'Apache-HttpClient/UNAVAILABLE (java 1.4)',
               'Connection':'Keep-Alive',
               'Host':'711-goodcall.api.tigerspike.com',
               'Authorization':'%s' % tssa,
               'X-OsVersion':ANDROID_VERSION,
               'X-OsName':'Android',
               'X-DeviceID':DEVICE_ID,
               'X-AppVersion':APP_VERSION}

    response = requests.get(BASE_URL + "store/StoresAfterDateTime/1001", headers=headers)

    return(response.content)

if __name__ == '__main__' :
    print("You should call the functions in this module from your main script")
