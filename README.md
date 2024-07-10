# criteo_uplift_model

[Scoring criteria](https://github.com/aleksandr-dzhumurat/mlops-zoomcamp/tree/main/07-project)

Delivery time prediction model trained on brazilian ecommerse dataset


First, prepare directory structure for data

```shell
make prepare-dirs
```

Download `.zip` archive from the [kaggle competition](
Download data from https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) and put to the directory data_store/dataset. 

Build and run docker image for local development
```shell
make run-dev
```

Run data extraction script

```shell
make prepare-data
```


# Set up MLFlow for an experiment tracking

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

Open [EDA](http://localhost:8899/notebooks/EDA.ipynb) and view charts and dasboards

Run params search. After script finished check [MLFlow](http://localhost:8000/)

```shell
make run params-search
```

Train and register best model
```shell
 make register-model
```

# Grafana monitoring

Backfill data and check dashboards in [grafana](http://localhost:3000/)

```shell
make backfill
```

Eval grafana dashboards

# Tests


/tests - unitests for ci/cd

```shell
make tests
```

/integration tests - for local usage

```shell
make integration-tests
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


Test from curl
```
curl -X POST http://127.0.0.1:8090/delivery_time \
    -H "Content-Type: application/json" \
    -d '{"seller_zip_code_prefix":12345, "customer_zip_code_prefix":54321, "delivery_distance_km":50}'
```