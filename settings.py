#! /usr/bin/python3

# API_KEY: Google Maps with Geocoding API Key
# Google Maps API is used to Geocode a Postcode to a logitude and latitude
# To use the API a private API key is required.
# Open the following URL (https://developers.google.com/maps/documentation/embed/get-api-key) to obtain a private API key
# Ensure you have enabled the "Geocoding API"

# The API_KEY is not needed as much anymore. It is only needed if you do not have a stores.json file where your script
# is running from. But it should be automatically downloaded on first run anyway. The stores.json file is used to
# determine the location of a 7Eleven stores and lock in around that area.

API_KEY=""

# TZ: All times are displayed using the chosen timezone. Choices for Australia are:
# Australia/ACT
# Australia/Adelaide
# Australia/Brisbane
# Australia/Broken_Hill
# Australia/Canberra
# Australia/Currie
# Australia/Darwin
# Australia/Eucla
# Australia/Hobart
# Australia/LHI
# Australia/Lindeman
# Australia/Lord_Howe
# Australia/Melbourne
# Australia/NSW
# Australia/North
# Australia/Perth
# Australia/Queensland
# Australia/South
# Australia/Sydney
# Australia/Tasmania
# Australia/Victoria
# Australia/West
# Australia/Yancowinna
TZ="UTC"

# BASE_URL: 7-11 Mobile Application API End Point
BASE_URL="https://711-goodcall.api.tigerspike.com/api/v1/"

# PRICE_URL: 11-Seven Price API
PRICE_URL="https://projectzerothree.info/api.php?format=json"

# Device name - Samsung Galaxy S10. You can change this to any device you want.
DEVICE_NAME="SM-G973FZKAXSA"

# OS version
OS_VERSION="Android 9.0.0"

# App version
APP_VERSION="1.10.0.2044"

# Device id - A 16 character hexadecimal device identifier. You can change this to your own device ID
# if you know it, otherwise a random one will be generated
DEVICE_ID=""
