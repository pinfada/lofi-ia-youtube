.PHONY: up down logs rebuild shell api worker

up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f

rebuild:
	docker compose build --no-cache

api:
	docker compose exec api bash

worker:
	docker compose exec worker bash
