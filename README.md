# python-fastapi

This is the repository for a containerized RESTful python api on the fastapi framework.

The api fetches records from the [Marvel API](https://developer.marvel.com/) and stores the results in a MySQL database.

More specifically the api gets marvel characters records. The http methods take care of displaying and storing information like the character names or character descriptions.

Aside from the CRUD like RESTful behavior provided, the python api has a websocket connection to show the external api results on [localhost:8000](https://localhost:8000/) (You'll have to wait a bit for the web socket connection to open)

# Steps to run locally

1. You will need to clone this repository:
    ```
    git clone https://github.com/jpuseche/python-fastapi.git
    ```

2. Start docker on your local machine. You'll need it to set the working environment of this project.

The easiest way to install docker is by downloading docker desktop [here](https://www.docker.com/products/docker-desktop/)

3. On the root directory of this project. Run the command to set up the docker containers:
    ```
    docker-compose up
    ```

With this you should be ready to run this site in your local machine.

# Endpoints
GET http://localhost:8000
Serves template to call web socket and display Marvel API data.
<img width="1192" alt="image" src="https://github.com/jpuseche/python-fastapi/assets/73227425/20853702-ac3e-4da6-ade6-0ed11c6cd809">

GET http://localhost:8000/api/data
Gets Marvel API characters records and displays them in a json format.
<img width="1120" alt="image" src="https://github.com/jpuseche/python-fastapi/assets/73227425/1921c914-81fe-4053-9b66-2b4564b1b487">

POST http://localhost:8000/api/data
Stores Marvel API characters records returning a status message.
The message will let you know wether there was an error or the request completed successfully.
<img width="1166" alt="image" src="https://github.com/jpuseche/python-fastapi/assets/73227425/76cef308-608b-498a-baf3-13ed04783bf9">

GET http://localhost:8000/api/data/{id}
Gets one specific Marvel API character record and displays it in a json format.
If the request is unable to find the record on the db, you'll get an error message as the result.
<img width="1163" alt="image" src="https://github.com/jpuseche/python-fastapi/assets/73227425/8aa74680-c434-4d38-b7ba-bbb617d39d44">

<img width="1121" alt="image" src="https://github.com/jpuseche/python-fastapi/assets/73227425/800b52e6-0ab9-427f-9b83-f1a92598016a">

<img width="1122" alt="image" src="https://github.com/jpuseche/python-fastapi/assets/73227425/14756f17-781a-4ef8-b3c4-882ce037512c">

# Used Tools

1. python: This project uses python for the api codebase. As it is a high level language and has a clear syntax to understand, it works wonders as a demonstration of the api logic.

2. fastapi: This is the python framework in which the api is set up.

3. mysql: The mysql database on this project is used to store and fetch marvel characters data records.

4. docker: This technology is used to containerize the api and mysql database and enable an easy use of this project locally.
