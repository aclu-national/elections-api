# Docker for the elections API

Based on [Flask on Docker](https://github.com/testdrivenio/flask-on-docker).

## First-time setup:

1. Rename *.env.dev-sample* to *.env.dev*.
1. Update the environment variables in *.env.dev*
1. Build the images and run the containers:

    ```sh
    docker-compose up -d --build
    ```

    Test it out at [http://localhost:5000](http://localhost:5000). The "elections-api" folder is mounted into the container and your code changes apply automatically.

## Development

To start the containers:
```sh
docker-compose up -d
```

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