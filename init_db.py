import mysql.connector
import os

# Method to get db connection
def getDBConn():
    conn = mysql.connector.connect(
        host=os.getenv('MYSQL_HOST'),
        db=os.getenv('MYSQL_DB'),
        user=os.getenv('MYSQL_USER'),
        port=os.getenv('MYSQL_PORT'),
        password=os.getenv('MYSQL_PASSWORD')
    )

    return conn

def dbInit():
    conn = mysql.connector.connect(
        host=os.getenv('MYSQL_HOST'),
        user=os.getenv('MYSQL_USER'),
        port=os.getenv('MYSQL_PORT'),
        password=os.getenv('MYSQL_PASSWORD')
    )

    # Creating a cursor object using the cursor() method
    cursor = conn.cursor()

    #Initialize db new instance
    cursor.execute('''DROP DATABASE IF EXISTS python_fastapi;
                    CREATE DATABASE python_fastapi;
                    USE python_fastapi;

                    DROP TABLE IF EXISTS characters;
                   
                    CREATE TABLE characters(
                        id SERIAL PRIMARY KEY,
                        marvel_id INT NOT NULL,
                        name VARCHAR(50) NOT NULL,
                        description TEXT,
                        modified DATE,
                        thumbnail_path VARCHAR(255),
                        thumbnail_extension VARCHAR(10)
                    );
                    ''')

    #Closing the connection
    conn.close()