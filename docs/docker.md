# Docker for the elections API

Based on [Flask on Docker](https://github.com/testdrivenio/flask-on-docker).

## First-time setup:

1. Rename *.env.dev-sample* to *.env.dev*.
1. Update the environment variables in *.env.dev*
1. Build the images and run the containers:

    ```sh
    docker-compose up -d --build
    ```

    Test it out at [http://localhost:5000](http://localhost:5000). The "elections-api" folder is mounted into the container and your code changes apply automatically. You may need to run `docker-compose up -d` one more time to ensure the api is running if this is your first time setting things up. 
    
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