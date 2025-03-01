import xml.etree.ElementTree as ET
#import urllib2
import requests
import xmltodict

user_agent       = 'HamPuff-QA/14.074/220213'
hampuff_url      = 'http://www.hamqsl.com/solarxml.php'
hampuff_headers  = {'User-Agent' : user_agent}
hampuff_request  = requests.get(hampuff_url, params=hampuff_headers)
hampuff_response = hampuff_request.text
my_dict          = xmltodict.parse(hampuff_response)

#calc_cond = my_dict['solar']['solardata']['calculatedconditions']
#band_cond = my_dict['solar']['solardata']['calculatedconditions']['@name="80m-40m"']['@time="night"']
#band_cond = my_dict['solar']['solardata']['calculatedconditions']['@name']
#band_cond = my_dict['solar']['solardata']['calculatedconditions']['band']['@name']['80m-40m']['@time']['day']
band_cond1 = my_dict['solar']['solardata']['calculatedconditions']['band'][0]['@name']['@time']
band_cond2 = my_dict['solar']['solardata']['calculatedconditions']['band'][0]['@time']

hampuff_data = "%s = %s" % ("band conditions", band_cond1)
print("Data set:\n\t%s" % band_cond1)
print("Data set:\n\t%s" % band_cond2)

