# python scripts/peerdb_py.py 14570
from rich import print 
import requests
import json
import sys
import os
requests.packages.urllib3.disable_warnings()

bgp_asn = sys.argv[1]
api_key = sys.argv[2]

# Get the value of the PEERDB_API_KEY environment variable
# api_key = os.environ.get("PEERDB_API_KEY")

# Check if the PEERDB_API_KEY variable exists
if api_key is not None:
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
else:
    print("PeeringDB API Key is not set.")

