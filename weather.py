import json
import urllib2

API_KEY = ""
with open("apikey.txt","r") as f:
	API_KEY = f.readline().strip()

url_yesterday = 'http://api.wunderground.com/api/%s/geolookup/yesterday/q/MI/Ann_Arbor.json' % API_KEY
url_forecast = 'http://api.wunderground.com/api/%s/geolookup/forecast/q/MI/Ann_Arbor.json' % API_KEY

yesterday = json.loads(urllib2.urlopen(url_yesterday).read())
forecast = json.loads(urllib2.urlopen(url_forecast).read())

prev_high = yesterday['history']['dailysummary'][0]['maxtempi']
today_high = forecast['forecast']['simpleforecast']['forecastday'][0]['high']['fahrenheit']

print "Yesterday's High Temperature:", prev_high
print "Today's High Temperature:", today_high
