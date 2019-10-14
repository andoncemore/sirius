run:
	docker-compose -f docker-compose.yml

run-development:
	docker-compose -f docker-compose.yml -f docker-compose.db.yml -f docker-compose.development.yml up

ci:
	docker-compose -f docker-compose.yml -f docker-compose.test.yml run --rm --entrypoint "nosetests" sirius

ci-snapshot-update:
	docker-compose -f docker-compose.yml -f docker-compose.test.yml run --rm --entrypoint "nosetests --snapshot-update" sirius