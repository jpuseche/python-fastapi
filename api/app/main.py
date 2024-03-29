from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import os
from dotenv import load_dotenv
import requests
import hashlib
from datetime import datetime
import mysql.connector

load_dotenv() # Load api env variables
app = FastAPI() # Initialize App

# ---------------------------------------------- url params --------------------------------------------- #
ts = datetime.now().strftime('%Y-%m-%d%H:%M:%S')
public_key = os.getenv('MARVEL_PUBLIC_KEY')
private_key = os.getenv('MARVEL_PRIVATE_KEY')
hash_key = hashlib.md5(f'{ts}{private_key}{public_key}'.encode('utf-8')).hexdigest()
params = {'orderBy':'name', 'limit':'100','ts': ts, 'apikey': public_key, 'hash': hash_key}
characters_url = 'https://gateway.marvel.com:443/v1/public/characters'
# ------------------------------------------------------------------------------------------------------- #

# Function to get connection to the containerized MySQL database
def get_db_conn():
    conn = mysql.connector.connect(
        host=os.getenv('MYSQL_HOST'),
        db=os.getenv('MYSQL_DB'),
        user=os.getenv('MYSQL_USER'),
        port=os.getenv('MYSQL_PORT'),
        password=os.getenv('MYSQL_PASSWORD')
    )

    return conn

# Function to convert characters directory to only contain relevant keys (fields)
def convert_to_pretty(characters):
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

# template where the WebSocket connection is going to be called from
marvel_main_template = """
<!DOCTYPE html>
<html>
    <head>
        <title>Marvel Api Data</title>
    </head>
    <body>
        <h1>Marvel Api Data</h1>
        <form action="" onsubmit="sendMessage(event)">
            <span>Click Submit to get Marvel Api Data</span>
            <button>Submit</button>
        </form>
        <div id='content-wrapper'>
        </div>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                var contentWrapper = document.getElementById('content-wrapper')
                var content = document.createTextNode(event.data)
                contentWrapper.appendChild(content)
            };
            function sendMessage(event) {
                ws.send(true)
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""

# Serving template in charge of sending the request to the web socket
@app.get("/")
async def get():
    return HTMLResponse(marvel_main_template)

# Web Socket to return Marvel API json
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            res = requests.get(characters_url, params=params) # Fetching Marvel API Data
        except Exception as err:
            error_msg = f'Error while calling marvel API: {err}'
            return error_msg

        if res.status_code == 200:
            res_json = res.json()

            characters = res_json['data']['results']
            characters_pretty = convert_to_pretty(characters) # Calling function to only show relevant fields
            
            await websocket.receive() # Needs to wait for socket to receive request data
            return await websocket.send_text(str(characters_pretty))
        
        else:
            error_msg = f'Failed to retrieve data from the marvel API. Status code: {res.status_code}'
            print(error_msg)

            await websocket.receive() # Needs to wait for socket to receive request data
            return await websocket.send_text(str(error_msg))

# Get method to return Marvel API json
@app.get("/api/data")
def get_api_data():
    try:
        res = requests.get(characters_url, params=params) # Fetching Marvel API Data
    except Exception as err:
        error_msg = f'Error while calling marvel API: {err}'
        return error_msg

    if res.status_code == 200:
        res_json = res.json()

        characters = res_json['data']['results']

        characters_pretty = convert_to_pretty(characters) # Calling function to only show relevant fields

        return characters_pretty
    
    else:
        error_msg = f'Failed to retrieve data from the marvel API. Status code: {res.status_code}'
        print(error_msg)

        return error_msg

# Post method to store Marvel API data
@app.post("/api/data")
def post_api_data():
    try:
        res = requests.get(characters_url, params=params) # Fetching Marvel API Data
    except Exception as err:
        error_msg = f'Error while calling marvel API: {err}'
        print(error_msg)
        return error_msg

    if res.status_code == 200:
        res_json = res.json()
        characters = res_json['data']['results']

        try:
            conn = get_db_conn()
            cursor = conn.cursor()

            for i in range(len(characters)):
                cursor.execute('''INSERT INTO characters (marvel_id, name, description, modified, thumbnail_path, thumbnail_extension) VALUES (%s, %s, %s, DATE_FORMAT(%s, '%Y-%m-%d'), %s, %s);''',
                            (characters[i]['id'],
                                characters[i]['name'],
                                characters[i]['description'],
                                characters[i]['modified'].partition('T')[0],
                                characters[i]['thumbnail']['path'],
                                characters[i]['thumbnail']['extension']))
                conn.commit() # Fetching database data
            
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

# Get method to return specific Marvel API record
@app.get("/api/data/{character_id}")
def get_api_data_character(character_id: int):
    try:
        conn = get_db_conn()
        cursor = conn.cursor()

        cursor.execute('''SELECT * FROM characters WHERE id = %s;''', (character_id,))
        character = cursor.fetchone() # Fetching database data
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