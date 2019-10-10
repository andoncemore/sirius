run-development:
	docker-compose -f docker-compose.yml -f docker-compose.db.yml -f docker-compose.development.yml up --build

ci:
	docker-compose -f docker-compose.yml -f docker-compose.test.yml run --rm --entrypoint nosetests sirius