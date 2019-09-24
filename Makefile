run-development:
	docker-compose -f docker-compose.yml -f docker-compose.db.yml -f docker-compose.development.yml up --build

run-test:
	docker rm -v sirius-database-test || true
	docker-compose -f docker-compose.yml -f docker-compose.test.yml up --build