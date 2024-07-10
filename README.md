# criteo_uplift_model
Uplift model trained on criteo dataset

https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

[Scoring criteria](https://github.com/aleksandr-dzhumurat/mlops-zoomcamp/tree/main/07-project)

Create env

```shell
brew install openssl xz gdbm &&
pyenv install 3.11 && \
pyenv virtualenv 3.11 criteo-env
```

Install python requirements
```
source ~/.pyenv/versions/criteo-env/bin/activate && \
pip install -r requirements.txt
```

# Train model

```shell
make prepare-dirs
```

```shell
python src/train_test_split.py
```

# Set up services

Postgres

```shell
make run-postgres
```

Terminate  Postgres, run MLFlow
```shell
make run-mlflow
```

Terminate ML flow, run Jupyter
```shell
make run-jupyter
```

Open [0.0.0.0:8899](http://0.0.0.0:8899/)

[Dataset](https://drive.google.com/drive/folders/1cuKmgr7OQDbeninjMudUzm32xWcb_Wg7)


https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce


```shell
DATA_PATH=$(pwd)/data_store/dataset python src/extract_data.py
```

```shell
docker-compose build service
```


```shell
docker-compose run service
```

```shell
docker exec -it ef395769ed2a python3 src/prepare_data.py /srv/src/config.yml
```

```shell
docker exec -it ef395769ed2a python3 src/hyperopt_params_search.py /srv/src/config.yml
```

```shell
docker exec -it ef395769ed2a pytest tests/
```


https://www.skytowner.com/explore/getting_started_with_dagster

```shell
pyenv install 3.10 && \
pyenv virtualenv 3.10 delivery-prediction-env && \
source ~/.pyenv/versions/delivery-prediction-env/bin/activate && \
pip install --upgrade pip && \
pip install -r dagster_requirements.txt
```

Materialization
http://localhost:3000/assets

# Tests

/tests - unitests for ci/cd
/integration tests - for local usage

# Backfill

Eval grafana dashboards

```shell
docker exec -it 0e7536d1d9b0 python3 src/batch_prediction_backfill.py /srv/src/config.yml
```

```shell
docker exec -it 711cba360a17 pytest integration_tests/
```

Create bucket
```shell
docker exec -it 3c63afa46b27 awslocal --endpoint-url=http://localhost:4566 s3 mb s3://delivery-prediction
```

```shell
docker exec -it 711cba360a17 pytest src/integration_tests/
```


Test from curl
```
curl -X POST http://127.0.0.1:8090/delivery_time \
    -H "Content-Type: application/json" \
    -d '{"seller_zip_code_prefix":12345, "customer_zip_code_prefix":54321, "delivery_distance_km":50}'
```