# Week 1 — App Containerization

## Required Homework

### Containerize the Application
We need to containerize both the Backend and the Frontend.

#### Containerizing the Backend
A Dockerfile is created [here: `backend-flask/Dockerfile`.](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/backend-flask/Dockerfile)

```dockerfile
FROM python:3.10-slim-buster

WORKDIR /backend-flask

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

ENV FLASK_ENV=development

EXPOSE ${PORT}
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=4567"]
```

To build the Backend Container I used the following command. 

```sh
docker build -t  backend-flask ./backend-flask
```
The Backend image was built successfuly

![Building the B-image](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/journal/assets/Build-Docker.PNG)

To Run the Backend Container I used the following command.

```sh
docker run --rm -p 4567:4567 -it -e FRONTEND_URL='*' -e BACKEND_URL='*' backend-flask
```

#### Containerizing the Frontend 

I have to run NPM Install before building the container since it needs to copy the contents of node_modules

```
cd frontend-react-js
npm i
```

Then I created a Dockerfile [here: `frontend-react-js/Dockerfile`.](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/frontend-react-js/Dockerfile)

```dockerfile
FROM node:16.18

ENV PORT=3000

COPY . /frontend-react-js
WORKDIR /frontend-react-js
RUN npm install
EXPOSE ${PORT}
CMD ["npm", "start"]
```
To build the Frontend Container I used the following command.

```sh
docker build -t frontend-react-js ./frontend-react-js
```
The Frontend image was built successfuly

![Building the F-image](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/journal/assets/Frontend-Docker-Build.PNG)

To run the Frontend Container I used the following command.

```sh
docker run -p 3000:3000 -d frontend-react-js
```
#### Getting Container Images 
To list all the container images in my Repo I called the following command.
```
docker images
```
![Images](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/journal/assets/Docker-images.PNG)

#### Getting Running Container Ids
To get all running containers I used the following command

```
docker ps
```
![running](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/journal/assets/Docker-run1.png)

#### Multiple Containers

To run the Backend and Frontend containers in the same time I created a docker-compose file

I created  [`docker-compose.yml`](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/docker-compose.yml) at the root of my project.

```yaml
version: "3.8"
services:
  backend-flask:
    environment:
      FRONTEND_URL: "https://3000-${GITPOD_WORKSPACE_ID}.${GITPOD_WORKSPACE_CLUSTER_HOST}"
      BACKEND_URL: "https://4567-${GITPOD_WORKSPACE_ID}.${GITPOD_WORKSPACE_CLUSTER_HOST}"
    build: ./backend-flask
    ports:
      - "4567:4567"
    volumes:
      - ./backend-flask:/backend-flask
  frontend-react-js:
    environment:
      REACT_APP_BACKEND_URL: "https://4567-${GITPOD_WORKSPACE_ID}.${GITPOD_WORKSPACE_CLUSTER_HOST}"
    build: ./frontend-react-js
    ports:
      - "3000:3000"
    volumes:
      - ./frontend-react-js:/frontend-react-js

# the name flag is a hack to change the default prepend folder
# name when outputting the image names
networks: 
  internal-network:
    driver: bridge
    name: cruddur
```

### Setting up the Notifications Endpoint

1. Adding the Notification Endpoint in the [OpenAI.yml](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/backend-flask/openapi-3.0.yml) file.
  
  ```yml
   /api/activities/notifications:
    get:
      description: 'Return a feed of all pepole who I follow'
      tags:
        - activities
      parameters: []
      responses:
        '200':
          description: Returns an array of activities
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Activity'
   ```

2. To Write a Flask Backend Endpoint for Notifications the file [backend-flask/app.py](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/backend-flask/app.py) is updated and a new [backend-flask/services/notifications_activities.py](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/backend-flask/services/notifications_activities.py) file is created as follows.

![Backend-notification](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/journal/assets/backend-notification.PNG)

![Backend-notification2](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/journal/assets/backend-notification2.PNG)


3. To Write a React Page for Notifications the file [frontend-react-js/src/App.js](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/frontend-react-js/src/App.js) is updated  as follows and two files [frontend-react-js/src/pages/NotificationsFeedPage.css](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/frontend-react-js/src/pages/NotificationsFeedPage.css) and [frontend-react-js/src/pages/NotificationsFeedPage.js](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/frontend-react-js/src/pages/NotificationsFeedPage.css) are created.

![Frontend-not](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/journal/assets/Frontend-notification.PNG)

Now we can see the Notifications page on Cruddur App.

![Notifications-page](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/journal/assets/Frontend%20notifications.PNG)

### Setting up Databases in our Container

The following lines are integrated into our existing [docker-compose](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/7e27f1f02ee73c4ac8ff5b1d688b395875bcbfe1/docker-compose.yml) file:

1. Running DynamoDB Local Container

```yaml
services:
  dynamodb-local:
    # https://stackoverflow.com/questions/67533058/persist-local-dynamodb-data-in-volumes-lack-permission-unable-to-open-databa
    # We needed to add user:root to get this working.
    user: root
    command: "-jar DynamoDBLocal.jar -sharedDb -dbPath ./data"
    image: "amazon/dynamodb-local:latest"
    container_name: dynamodb-local
    ports:
      - "8000:8000"
    volumes:
      - "./docker/dynamodb:/home/dynamodblocal/data"
    working_dir: /home/dynamodblocal
```

2. Running Postgres Container 
 
```yaml
services:
  db:
    image: postgres:13-alpine
    restart: always
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    ports:
      - '5432:5432'
    volumes: 
      - db:/var/lib/postgresql/data
volumes:
  db:
    driver: local
```

To install the postgres client into Gitpod the [.gitpod.yml](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/7e27f1f02ee73c4ac8ff5b1d688b395875bcbfe1/.gitpod.yml) file is updated with the following lines:

```sh
  - name: postgres
    init: |
      curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc|sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/postgresql.gpg
      echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" |sudo tee  /etc/apt/sources.list.d/pgdg.list
      sudo apt update
      sudo apt install -y postgresql-client-13 libpq-dev
```



## Homework Challenges:

### Healthckeck in docker-compose file

I tried to implement a healthcheck in a docker-compose file according to [this reference](https://howchoo.com/devops/how-to-add-a-health-check-to-your-docker-container). I created a small project named [docker-healthcheck](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/tree/main/journal/assets/docker-healthcheck). 

I started with the [requirements.txt](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/journal/assets/docker-healthcheck/requirements.txt):
```
Flask==0.12.2
```

Then the [Dockerfile](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/journal/assets/docker-healthcheck/Dockerfile):

``` Dockerfile
FROM python:3.6-alpine

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

CMD ["python", "app.py"]
```

And the [app.py](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/journal/assets/docker-healthcheck/app.py):

```py
from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello world'


if __name__ == '__main__':
    app.run(host='0.0.0.0')
```
I specified the health check settings in the [docker-compose](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/journal/assets/docker-compose.yml) file as follows:

```yml
version: '3.1'

services:
  web:
    image: docker-flask
    ports:
      - '5000:5000'
    healthcheck:
      test: curl --fail -s http://localhost:5000/ || exit 1
      interval: 1m30s
      timeout: 10s
      retries: 3
```

And verified if it's working:

![Healthcheck](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/journal/assets/inspect-healthcheck.png)
