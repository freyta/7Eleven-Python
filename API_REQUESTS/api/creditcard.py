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

def getCreditCards(deviceSecret, accessToken):

    tssa = generateTssa(BASE_URL + "CreditCard/List", "GET", "", accessToken)

    headers = {'User-Agent':'Apache-HttpClient/UNAVAILABLE (java 1.4)',
               'Connection':'Keep-Alive',
               'Host':'711-goodcall.api.tigerspike.com',
               'Authorization':'%s' % tssa,
               'X-OsVersion':ANDROID_VERSION,
               'X-OsName':'Android',
               'X-DeviceID':DEVICE_ID,
               'X-AppVersion':APP_VERSION,
               'X-DeviceSecret':deviceSecret}

    response = requests.get(BASE_URL + "CreditCard/List", headers=headers)

    returnContent = json.loads(response.content)

    ccID = returnContent[0]['Id']
    MaskPan = returnContent[0]['MaskPan']

    return ccID, MaskPan


def beginCCTransaction(creditcardId, amount, deviceSecret, accessToken):

    payload = '{"CreditCardId":"' + creditcardId + '","Amount":"' + amount + '"}'
    tssa = generateTssa(BASE_URL + "GiftCard/StartTopUp2", "POST", payload, accessToken)

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

    response = requests.post(BASE_URL + "GiftCard/StartTopUp2", data=payload, headers=headers)

    returnContent = json.loads(response.content)

    TraceId = returnContent['TraceId']
    PayUrl = returnContent['PayUrl']

    return TraceId, PayUrl

def verifyCcTransaction(cvv, traceId, payurl, deviceSecret, accessToken):

    payload = '{"ccv":"' + str(cvv) + '","traceId":"' + traceId + '","requestOrigin":"MOBILE"}'

    tssa = generateTssa(payurl, "POST", payload, accessToken)

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

    response = requests.post(payurl, data=payload, headers=headers)

    return(response.content)


def confirmCreditCardTransaction(TraceId, MaskedPan, deviceSecret, accessToken):

    payload = '{"TraceId":"' + TraceId + '","MaskedPan":"' + MaskedPan + '"}'
    tssa = generateTssa(BASE_URL + "GiftCard/ConfirmTopUp", "POST", payload, accessToken)

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

    response = requests.post(BASE_URL + "GiftCard/ConfirmTopUp", data=payload, headers=headers)

    return(response.content)


# TODO: Add credit card registration
#def beginCreditCardRegistration()

if __name__ == '__main__' :
    print("You should call the functions in this module from your main script")
