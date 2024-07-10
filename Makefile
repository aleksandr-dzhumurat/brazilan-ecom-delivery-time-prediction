CURRENT_DIR = $(shell pwd)
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

push-ui: build-prod
	docker push adzhumurat/delivery_time_prediction:latest

run-prod:
	docker run -p 8090:8090 -it --rm adzhumurat/delivery_time_prediction:latest