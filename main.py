from fastapi import FastAPI
import requests
import hashlib
import datetime
import ssl

class TLSAdapter(requests.adapters.HTTPAdapter):

    def init_poolmanager(self, *args, **kwargs):
        ctx = ssl.create_default_context()
        ctx.set_ciphers('DEFAULT@SECLEVEL=1')
        kwargs['ssl_context'] = ctx
        return super(TLSAdapter, self).init_poolmanager(*args, **kwargs)

app = FastAPI()

ts = datetime.datetime.now().strftime('%Y-%m-%d%H:%M:%S')
public_key = '3ac56effcbb04ef969083437500e3007'
private_key = '6b2cd81495cc39a50ec32e5f54ebf1b1ec18755a'
hash_key = str(hashlib.md5((ts+private_key+public_key).encode('utf-8')))

def hash_params():
    """ Marvel API requires server side API calls to include
    md5 hash of timestamp + public key + private key """

    hash_md5 = hashlib.md5()
    hash_md5.update(f'{ts}{private_key}{public_key}'.encode('utf-8'))
    hashed_params = hash_md5.hexdigest()

    return hashed_params

@app.get("/api/data")
def api_data():
    params = {'orderBy':'name', 'limit':'100','ts': ts, 'apikey': public_key, 'hash': hash_params()}
    marvel_characters = 'https://gateway.marvel.com:443/v1/public/characters'

    session = requests.session()
    session.mount('https://', TLSAdapter())
    res = session.get(marvel_characters, params=params)

    if res.status_code == 200:
        res_json = res.json()

        results = res_json['data']['results']

        pretty_results_total = []
        for i in range(len(results)):
            pretty_results = {}
            pretty_results['id'] = results[i]['id']
            pretty_results['name'] = results[i]['name']
            pretty_results['description'] = results[i]['description']
            pretty_results['modified'] = results[i]['modified']
            pretty_results['thumbnail'] = results[i]['thumbnail']
            pretty_results['comics'] = results[i]['comics']

            pretty_results_total.append(pretty_results)

        return pretty_results_total
    
    else:
        print("Failed to retrieve data from the marvel API. Status code:", res.status_code)