import json
import urllib.request
import os

checkwx_api_key = os.getenv("CHECKWX_API_KEY", "changeme")
user_agent = 'AirPuff/2.0; Python/3.6.8'

def get_data(airport_code):
    airport_csv_lowercase = airport_code.lower()
    met_url = f'https://api.checkwx.com/metar/{airport_csv_lowercase}/decoded?pretty=1'
    met_hdrs = {
        'X-API-Key': checkwx_api_key,
        'User-Agent': user_agent
    }
    met_req = urllib.request.Request(met_url, headers=met_hdrs)
    met_res = urllib.request.urlopen(met_req)
    met_data = met_res.read().decode('utf-8')
    met_json = json.loads(met_data)
    return met_json

