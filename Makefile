CURRENT_DIR = $(shell pwd)
DEV_ENV = $(shell docker ps --filter "name=dev-run" --format "{{.ID}}")
LOCALSTACK_ENV = $(shell docker ps --filter "name=localstack" --format "{{.ID}}")
include .env
export

prepare-dirs:
	mkdir -p ${CURRENT_DIR}/data_store/postgres_data || true && \
	mkdir -p ${CURRENT_DIR}/data_store/minio || true && \
    mkdir -p ${CURRENT_DIR}/data_store/mlflow || true && \
    mkdir -p ${CURRENT_DIR}/data_store/dataset || true && \
    mkdir -p ${CURRENT_DIR}/data_store/grafana || true && \
    mkdir -p ${CURRENT_DIR}/data_store/postgres_data || true

clear-dirs:
	rm -rf ${CURRENT_DIR}/data_store/postgres_data || true

run-dev:
	docker-compose run -d dev

down-dev:
	docker-compose down; docker rm -f ${DEV_ENV} 

prepare-data:
	docker exec -it ${DEV_ENV} python3 src/prepare_data.py /srv/src/config.yml

params-search:
	docker exec -it ${DEV_ENV} python3 src/hyperopt_params_search.py /srv/src/config.yml

register-model:
	docker exec -it ${DEV_ENV} python3 src/register_model.py /srv/src/config.yml

tests:
	docker exec -it ${DEV_ENV} pytest src/tests/

integration-tests:
	docker exec -it ${LOCALSTACK_ENV} awslocal --endpoint-url=http://localhost:4566 s3 mb s3://delivery-prediction && \
	docker exec -it ${DEV_ENV} pytest src/integration_tests/

backfill:
	docker exec -it ${DEV_ENV} python3 src/batch_prediction_backfill.py /srv/src/config.yml

pipfreeze:
	docker exec -it ${DEV_ENV} pip freeze

run-prefect:
	prefect server start

run-mlflow:
	docker-compose --env-file .env up mlflow

run-postgres:
	docker-compose --env-file .env up postgres

run-jupyter:
	docker-compose --env-file .env up jupyter

run-dagster:
	dagster-webserver -m services.dagster_code

build-prod:
	docker build -f ${CURRENT_DIR}/services/production/Dockerfile -t adzhumurat/delivery_time_prediction:latest .

prepare-prod: build-prod
	docker push adzhumurat/delivery_time_prediction:latest

run-prod:
	docker run -p 8090:8090 -it --rm adzhumurat/delivery_time_prediction:latest