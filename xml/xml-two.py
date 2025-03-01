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

print("XML = %s" % my_dict)

#tree = ET.parse(hampuff_response)
#root = tree.getroot()
#for child in root.iter():
   #print(child.tag, child.attrib)
   #print(child.tag)

