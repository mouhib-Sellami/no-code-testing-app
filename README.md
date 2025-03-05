# APP DOCS

`THE APP STILL UNDER DEVOLEPMENT.`

## Prerequisites

Before using this Makefile, ensure you have the following installed:
- Docker
- Docker compose
- WSL
- make (apt install make)
- A `compose.yaml` file in the same directory as this Makefile, defining the services (including a service named `server_container` for the Django app).

## Available Commands

| Command             | Description                                                                 |
|---------------------|-----------------------------------------------------------------------------|
| `make up`           | Starts all services defined in `compose.yaml` in the foreground.            |
| `make build`        | Builds or rebuilds all services in `compose.yaml`.                          |
| `make start`        | Starts all services in detached mode (background).                          |
| `make stop`         | Stops all running services.                                                 |
| `make status`       | Displays the status of all services.                                        |
| `make restart`      | Stops and restarts all services in detached mode.                           |
| `make logs`         | Shows the last 100 lines of logs for all services and follows them.         |
| `make server-logs`  | Shows the last 100 lines of logs for the Django container and follows them. |
| `make clean`        | Stops and removes all containers, networks, and volumes (requires confirmation). |
| `make sh`           | Opens a shell inside the Django container.                                  |
| `make make-migrations` | Generates Django migration files based on model changes.                  |
| `make migrate`      | Applies pending Django migrations to the database.                          |
| `make migration`    | Runs both `makemigrations` and `migrate` sequentially.                      |
| `make deploy-server`| Runs migrations and collects static files for deployment.                   |
| `make django`       | Runs a custom Django management command (e.g., `make django c="shell"`).    |
