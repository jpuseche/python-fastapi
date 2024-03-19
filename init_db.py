import mysql.connector

# Adding db connection configuration
def getDBConn():
    conn = mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        port='3306',
        password='123456789'
    )

    return conn

def dbInit():
    # Creating a cursor object using the cursor() method
    conn = getDBConn()
    cursor = conn.cursor()

    #Initialize db new instance
    cursor.execute('''DROP DATABASE IF EXISTS python_fastapi;
                    CREATE DATABASE python_fastapi;
                    USE python_fastapi;

                    DROP TABLE IF EXISTS characters;
                   
                    CREATE TABLE characters(
                        id INT NOT NULL PRIMARY KEY,
                        name VARCHAR(50) NOT NULL,
                        description TEXT,
                        modified DATE,
                        thumbnail_path VARCHAR(255),
                        thumbnail_extension VARCHAR(10)
                    );
                    ''')

    #Closing the connection
    conn.close()