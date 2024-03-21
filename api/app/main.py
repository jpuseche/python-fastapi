from fastapi import FastAPI
import os
from dotenv import load_dotenv
import requests
import hashlib
from datetime import datetime
import mysql.connector

load_dotenv()
app = FastAPI()

# ---------------------------------------------- url params --------------------------------------------- #
ts = datetime.now().strftime('%Y-%m-%d%H:%M:%S')
public_key = os.getenv('MARVEL_PUBLIC_KEY')
private_key = os.getenv('MARVEL_PRIVATE_KEY')
hash_key = hashlib.md5(f'{ts}{private_key}{public_key}'.encode('utf-8')).hexdigest()
params = {'orderBy':'name', 'limit':'100','ts': ts, 'apikey': public_key, 'hash': hash_key}
characters_url = 'https://gateway.marvel.com:443/v1/public/characters'
# ------------------------------------------------------------------------------------------------------- #
    
def getDBConn():
    conn = mysql.connector.connect(
        host=os.getenv('MYSQL_HOST'),
        db=os.getenv('MYSQL_DB'),
        user=os.getenv('MYSQL_USER'),
        port=os.getenv('MYSQL_PORT'),
        password=os.getenv('MYSQL_PASSWORD')
    )

    return conn

@app.get("/api/data")
def get_api_data():
    try:
        res = requests.get(characters_url, params=params)
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
                'thumbnail': characters[i]['thumbnail']
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
        res = requests.get(characters_url, params=params)
    except Exception as err:
        error_msg = f'Error while calling marvel API: {err}'
        print(error_msg)
        return error_msg

    if res.status_code == 200:
        res_json = res.json()
        characters = res_json['data']['results']

        try:
            conn = getDBConn()
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
            print(error_msg)
            return error_msg

        info_msg = f'Saved {len(characters)} character records successfully into database. Status code: {res.status_code}'
        print(info_msg)

        return info_msg
    else:
        error_msg = f'Failed to save data from the marvel API into db. Status code: {res.status_code}'
        print(error_msg)

        return error_msg
    
@app.get("/api/data/{character_id}")
def get_api_data_character(character_id: int):
    try:
        conn = getDBConn()
        cursor = conn.cursor()

        cursor.execute('''SELECT * FROM characters WHERE id = %s;''', (character_id,))
        character = cursor.fetchone()
        conn.close()

        character_dir = {
            'id': character[0],
            'marvelId': character[1],
            'name': character[2],
            'description': character[3],
            'modified': character[4],
            'thumbnail': {
                'path': character[5],
                'extension': character[6],
            }
        }

        return character_dir
    except Exception as err:
        error_msg = f'Error while getting character from db: {err}'
        print(error_msg)
        return error_msg