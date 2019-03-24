import hashlib
import hmac
import base64
import time
import sys
import uuid
import requests
import json
import random
import googlemaps

ANDROID_VERSION = "Android 9.0.0"
APP_VERSION = "1.7.0.2009"
DEVICE_NAME = "OnePlus ONEPLUS A0001"
BASE_URL = "https://711-goodcall.api.tigerspike.com/api/v1/"
# Generate a random Device ID
DEVICE_ID = ''.join(random.choice('0123456789abcdef') for i in range(15))

# Used to decrypt the encryption keys
def getKey(encryptedKey):
  # get the hex from the encrypted secret key and then split every 2nd character into an array row
  hex_string = hashlib.sha1("om.sevenel").hexdigest()
  hex_array = [hex_string[i:i+2] for i in range(0,len(hex_string),2)]

  # Key is the returned key
  key = ""
  i = 0
  # While i is less than the key or key2 array
  while(i < len(encryptedKey)):
    length = i%(len(hex_array))
    key += chr( int(hex_array[length], 16) ^ int ( encryptedKey[i] ))

    i = i + 1
  return key

# key is the OBFUSCATED_APP_ID
key  = getKey([36, 132, 5, 129, 42, 105, 114, 152, 34, 137, 126, 125, 93, 11, 117, 200, 157, 243, 228, 226, 40, 210, 84, 134, 43, 56, 37, 144, 116, 137, 43, 45])
# key2 is the OBFUSCATED_API_ID
key2 = getKey([81, 217, 3, 192, 45, 88, 67, 253, 91, 164, 110, 13, 28, 57, 22, 225, 246, 233, 153, 224, 87, 152, 65, 253, 2, 115, 83, 197, 64, 156, 94, 41, 25, 27, 116, 153, 150, 161, 188, 166, 113, 130, 83, 143])
key2 = base64.b64decode(key2)

# Generate the TSSA
def generateTssa(URL, method, payload = None, accessToken = None):

    # Replace the https URL with a http one and convert the URL to lowercase
    URL       = URL.replace("https", "http").lower()
    # Get a timestamp and a UUID
    timestamp = int(time.time())
    uuidVar   = str(uuid.uuid4())
    # Join the variables into 1 string
    str3      = key + method + URL + str(timestamp) + uuidVar
    # If we have a payload to encrypt, then we encrypt it and add it to str3
    if(payload):
        payload = base64.b64encode(hashlib.md5(payload).digest())
        str3   += payload
    signature = base64.b64encode(hmac.new(key2, str3, digestmod=hashlib.sha256).digest())

    # Finish building the tssa string
    tssa = "tssa 4d53bce03ec34c0a911182d4c228ee6c:" + signature + ":" + uuidVar + ":" + str(timestamp)
    # If we have an access token append it to the tssa string
    if(accessToken):
        tssa += ":" + accessToken

    return tssa
