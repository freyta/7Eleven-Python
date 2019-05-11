# 7-Eleven Python
What is this program? This is an extremely simple program to use that lets you lock in a fuel price from the comfort of your computer. Using this is easier than using the mock location removed APK that is floating around the internet because you do not need to use any other apps to fake a GPS location, and it universally works whether you are using an iPhone or an Android device! 7-Eleven Python will also automatically lock in the maximum amount of fuel that you are allowed to lock in. For instance if you have $38.97 in your account and fuel costs $1.13 a litre you will be able to lock in 35 litres.

# Setup
Download Python3 from http://python.org/downloads/, and install it on your computer. It is a good idea to add Python to your PATH file after installing it, this makes it easier to run Python from any folder.

You will need to install the dependencies in requirements.txt, you can use pip as follows `pip install -r requirements.txt`

You will also need a [Google Maps API key](https://developers.google.com/maps/documentation/embed/get-api-key), with the 'Geocoding API' enabled. You must set this key in settings.py or using the `API_KEY` environment variable.

# Usage
Very simple to use, run the program with either of the following commands `python3 app.py` or  `python app.py`. After you have started the program all you have to do is open your web browser and navigate to `http://[your-local-ip-address]:5000` i.e. `http://192.168.1.100:5000`. Then simply login with your 7-Eleven email and password, and click either automatic lock in or manually enter a postcode that you want to lock in from.

# Docker Usage
Clone the Git repo to your Docker host and build the image:

`docker build -t fuellock .`

Then run the image in a container:

<pre><code>docker run -d \<br />
  -e API_KEY=YOUR_GOOGLE_API_KEY \<br />
  -p 5000:5000 \<br />
  fuellock<br /></code></pre>

And browse to http://[Docker host IP]:5000

Other environment variables you can specify at runtime:

`BASE_URL`: The URL for the 7-Eleven API.<br />
`PRICE_URL`: The URL for the fuel price API (currently defaults to the API at projectzerothree.info)<br />
`DEVICE_NAME`: The name of the device reported on login to the 7-Eleven API (set by default in settings.py)<br />
`OS_VERSION`: The Android OS version reported on login to the 7-Eleven API (set by default in settings.py)<br />
`APP_VERSION`: The 7-Eleven app version reported on login to the 7-Eleven API (set by default in settings.py)
