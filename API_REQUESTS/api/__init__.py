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

import hashlib
import hmac
import base64
import time
import sys
import uuid
import requests
import json
import random

ANDROID_VERSION = "Android 9.0.0"
APP_VERSION = "1.10.0.2044"
DEVICE_NAME = "OnePlus ONEPLUS A0001"
BASE_URL = "https://711-goodcall.api.tigerspike.com/api/v1/"
# Generate a random Device ID
DEVICE_ID = ''.join(random.choice('0123456789abcdef') for i in range(15))

# Used to decrypt the encryption keys
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

# Encryption key used for the TSSA
encryption_key = bytes(base64.b64decode(getKey()))

# Generate the TSSA
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
