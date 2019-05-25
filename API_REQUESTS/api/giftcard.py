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

def getDigitalCardBalance(deviceSecret, accessToken):

    tssa = generateTssa(BASE_URL + "GiftCard/Balance", "GET", "", accessToken)

    headers = {'User-Agent':'Apache-HttpClient/UNAVAILABLE (java 1.4)',
               'Connection':'Keep-Alive',
               'Host':'711-goodcall.api.tigerspike.com',
               'Authorization':'%s' % tssa,
               'X-OsVersion':ANDROID_VERSION,
               'X-OsName':'Android',
               'X-DeviceID':DEVICE_ID,
               'X-AppVersion':'1.7.0.2009',
               'X-DeviceSecret':deviceSecret}

    response = requests.get(BASE_URL + "GiftCard/Balance", headers=headers)

    return(response.content)

def getPhysicalCardBalance(deviceSecret, accessToken, GiftCardNumber, GiftCardPin):

    payload = '{"GiftCardNumber":' + GiftCardNumber + ',"GiftCardPin":"' + GiftCardPin + '"}'
    tssa = generateTssa(BASE_URL + "GiftCard/PhysicalBalance", "POST", payload, accessToken)

    headers = {'User-Agent':'Apache-HttpClient/UNAVAILABLE (java 1.4)',
               'Connection':'Keep-Alive',
               'Host':'711-goodcall.api.tigerspike.com',
               'Authorization':'%s' % tssa,
               'X-OsVersion':ANDROID_VERSION,
               'X-OsName':'Android',
               'X-DeviceID':DEVICE_ID,
               'X-AppVersion':'1.7.0.2009',
               'X-DeviceSecret':deviceSecret,
               'Content-Type':'application/json; charset=utf-8'}

    response = requests.get(BASE_URL + "GiftCard/PhysicalBalance", headers=headers)

    return(response.content)



if __name__ == '__main__' :
    print("You should call the functions in this module from your main script")
