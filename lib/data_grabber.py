import json
import urllib.request

checkwx_api_key   = 'c5d65ffd02f05ddc608d5f0850'
user_agent        = 'AirPuff/2.0; Python/3.6.8'

def get_data(airport_list):
    ap_csv_lo         = airport_list.lower()
    ap_csv_up         = airport_list.upper()
    ap_list           = airport_list.split(",")

    # Get data
    met_url           = 'https://api.checkwx.com/metar/' + ap_csv_lo + '/decoded?pretty=1'
    met_hdrs          = {'X-API-Key'  : checkwx_api_key,
        'User-Agent' : user_agent }
    met_req           = urllib.request.Request(met_url, headers=met_hdrs)
    met_res           = urllib.request.urlopen(met_req)
    met_data          = met_res.read().decode('utf-8')
    #met_dump          = json.dumps(met_data)
    met_json          = json.loads(met_data)
    met_json_results  = met_json['results']
    #return met_json_results
    return met_json

