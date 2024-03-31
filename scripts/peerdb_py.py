import requests
import json
from rich import print 
import sys

bgp_asn = sys.argv[1]
api_key = ''

url = f'https://www.peeringdb.com/api/net?asn={bgp_asn}&key={api_key}'

response = requests.get(url)
response.raise_for_status() 
resp_data = response.json()

peer_info = resp_data.get('data', '')[0]
# print(peer_info)

v4prefixes = peer_info.get('info_prefixes4')
v6prefixes = peer_info.get('info_prefixes6')

print(v4prefixes)
print(v6prefixes)