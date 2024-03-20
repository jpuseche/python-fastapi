from fastapi import FastAPI
import os
from dotenv import load_dotenv
import init_db
import requests
import hashlib
from datetime import datetime
import session_manager

app = FastAPI()

load_dotenv()
init_db.dbInit()

# ---------------------------------------------- url params --------------------------------------------- #
ts = datetime.now().strftime('%Y-%m-%d%H:%M:%S')
public_key = os.getenv('MARVEL_PUBLIC_KEY')
private_key = os.getenv('MARVEL_PRIVATE_KEY')
hash_key = hashlib.md5(f'{ts}{private_key}{public_key}'.encode('utf-8')).hexdigest()
params = {'orderBy':'name', 'limit':'100','ts': ts, 'apikey': public_key, 'hash': hash_key}
characters_url = 'https://gateway.marvel.com:443/v1/public/characters'
# ------------------------------------------------------------------------------------------------------- #

@app.get("/api/data")
def get_api_data():
    try:
        session = requests.session()
        session.mount('https://', session_manager.TLSAdapter())
        res = session.get(characters_url, params=params)
    except Exception as err:
        error_msg = f'Error while calling marvel API: {err}'
        return error_msg

    if res.status_code == 200:
        res_json = res.json()

        characters = res_json['data']['results']

        characters_pretty = []
        for i in range(len(characters)):
            character = {
                'id': characters[i]['id'],
                'name': characters[i]['name'],
                'description': characters[i]['description'],
                'modified': characters[i]['modified'],
                'thumbnail': characters[i]['thumbnail'],
                'comics': characters[i]['comics'],
            }

            characters_pretty.append(character)

        return characters_pretty
    
    else:
        error_msg = f'Failed to retrieve data from the marvel API. Status code: {res.status_code}'
        print(error_msg)

        return error_msg

@app.post("/api/data")
def post_api_data():
    try:
        session = requests.session()
        session.mount('https://', session_manager.TLSAdapter())
        res = session.get(characters_url, params=params)
    except Exception as err:
        error_msg = f'Error while calling marvel API: {err}'
        return error_msg

    if res.status_code == 200:
        res_json = res.json()
        characters = res_json['data']['results']

        try:
            conn = init_db.getDBConn()
            cursor = conn.cursor()

            for i in range(len(characters)):
                cursor.execute('''INSERT INTO characters (marvel_id, name, description, modified, thumbnail_path, thumbnail_extension) VALUES (%s, %s, %s, DATE_FORMAT(%s, '%Y-%m-%d'), %s, %s);''',
                            (characters[i]['id'],
                                characters[i]['name'],
                                characters[i]['description'],
                                characters[i]['modified'].partition('T')[0],
                                characters[i]['thumbnail']['path'],
                                characters[i]['thumbnail']['extension']))
                conn.commit()
            
            conn.close()
        except Exception as err:
            error_msg = f'Error while saving character records: {err}'
            return error_msg

        info_msg = f'Saved {len(characters)} character records successfully into database. Status code: {res.status_code}'
        print(info_msg)

        info_msg = f'Saved marvel characters data successfully into database. Status code: {res.status_code}'
        print(info_msg)

        return info_msg
    else:
        error_msg = f'Failed to save data from the marvel API into db. Status code: {res.status_code}'
        print(error_msg)

        return error_msg
    
@app.get("/api/data/{character_id}")
def get_api_data_character(character_id: int):
    try:
        conn = init_db.getDBConn()
        cursor = conn.cursor()

        cursor.execute('''SELECT * FROM characters WHERE id = %s;''', (character_id,))
        character = cursor.fetchone()
        conn.close()

        character_dir = {
            'id': character[0],
            'name': character[1],
            'description': character[2],
            'modified': character[3],
            'thumbnail': character[4],
            'comics': character[5]
        }

        return character_dir
    except Exception as err:
        error_msg = f'Error while getting character from db: {err}'
        return error_msg