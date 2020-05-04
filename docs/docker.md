# Docker for the elections API

Based on [Flask on Docker](https://github.com/testdrivenio/flask-on-docker).

## First-time setup:

1. Install [Docker](https://download.docker.com/mac/stable/Docker.dmg)
1. You may need to update your Docker Desktop app by going to Preferences > Resources > File sharing, and adding the path to where this repo is on your computer
1. Rename *.env.dev-sample* to *.env.dev*.
1. Update *.env.dev* with the API keys for `GOOGLE_API_KEY` and `IPSTACK_API_KEY`
1. Build the images and run the containers:

    ```sh
    docker-compose up -d --build
    ```

    Test it out at [http://localhost:5000](http://localhost:5000). The "elections-api" folder is mounted into the container and your code changes apply automatically. You may need to run `docker-compose up -d` one more time to ensure the api is running if this is your first time setting things up. 
1. In order to load content into the database you'll need to:
    - go inside the `elections-api` container: `docker-compose exec elections-api /bin/bash`
    - and run `make all` in the following directories, in this order:
        1. `/sources`
        1. `/data`
        1. `/elections-api-private`
        1. `/`
1. In order to set up the `/v2/pip` endpoint, you'll also need to run `make election_races && make election_candidates && make targeted` from the root. 

Note: We have not set up `x-forwarded-for` in the docker container yet, so in order to use the `/v2/geoip` endpoint, you'll need to explicity pass an IP address as a query param (https://localhost:5000/v2/geoip?ip=xx.xxx.xxx.xx)
    
## Development
To start the containers:
```sh
docker-compose up -d
```

To list the containers that are currently running:
```sh
docker ps
```
You'd expect to see two containers listed here if everything is up and running correctly. One for the API and one for the database.

To stop the containers:
```sh
docker-compose stop
```

To remove the containers and their volumes:
```sh
docker-compose down -v
```

To open a shell inside a container that is already running:
```sh
docker-compose exec elections-api /bin/bash
```
You'll need to be inside the container to run all `make` commands.