DJANGO_CONTAINER_NAME = server_container

DJANGO_CONTAINER = $(DOCKER_COMPOSE) exec $(DJANGO_CONTAINER_NAME)

DJANGO_PYTHON = @$(DJANGO_CONTAINER) python3

DJANGO_MANAGER = @$(DJANGO_PYTHON) manage.py

DOCKER_COMPOSE = docker-compose

DOCKER_COMPOSE_FILE = compose.yaml

up:
	@$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) up $(c)

build:
	@$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) build $(c)

start:
	@$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) up -d $(c)

stop:
	@$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) stop $(c)

status:
	@$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) ps

restart:
	@$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) stop $(c)
	@$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) up $(c) -d

logs:
	@$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) logs --tail=100 -f $(c)

server-logs:
	@$(DOCKER_COMPOSE) logs $(DJANGO_CONTAINER_NAME) --tail=100 -f $(c)

clean: confirm
	@$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) down

sh:
	@$(DJANGO_CONTAINER) sh

make-migrations:
	@$(DJANGO_PYTHON) manage.py makemigrations

migrate:
	@$(DJANGO_PYTHON) manage.py migrate

migration:
	@$(DJANGO_PYTHON) manage.py makemigrations
	@$(DJANGO_PYTHON) manage.py migrate

deploy-server:
	@$(DJANGO_PYTHON) manage.py makemigrations
	@$(DJANGO_PYTHON) manage.py migrate
	@$(DJANGO_PYTHON) manage.py collectstatic

django:
	@$(eval c ?=)
	@$(DJANGO_MANAGER) $(c)