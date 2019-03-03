# 7-Eleven Python
What is this program? This is an extremely simple program to use that lets you lock in a fuel price from the comfort of your computer. Using this is easier than using the mock location removed APK that is floating around the internet because you do not need to use any other apps to fake a GPS location, and it universally works whether you are using an iPhone or an Android device! 7-Eleven Python will also automatically lock in the maximum amount of fuel that you are allowed to lock in. For instance if you have $38.97 in your account and fuel costs $1.13 a litre you will be able to lock in 35 litres.

# Setup
You will need to install the dependencies in requirements.txt, you can use pip as follows `pip install -r requirements.txt`

You will also need a [Google Maps API key](https://developers.google.com/maps/documentation/embed/get-api-key), with the 'Geocoding API'
 enabled.
After you have a Google Maps API key you will need to edit line 42 of app.py replacing the word **changethis** with your API key.

# Usage
Very simple to use, run the program with either of the following commands `python2.7 app.py` or if you use Python2.7 by default `python app.py`. After you have started the program all you have to do is login with your 7-Eleven email and password, and click either automatic lock in or manually enter a postcode that you want to lock in from.
