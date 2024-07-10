
from datetime import datetime

import pandas as pd

from utils import save_data, read_data

import os
import pandas as pd
from datetime import datetime

import boto3

import pytest

# Configure the Boto3 client to use LocalStack
s3 = boto3.client(
    's3',
    endpoint_url='http://localstack:4566',
    aws_access_key_id='test',
    aws_secret_access_key='test',
    region_name='us-east-1'
)

def list_objects_with_sizes(bucket_name, file_name):
    print('Searching for %s...' % file_name)
    response = s3.list_objects_v2(Bucket=bucket_name)
    if 'Contents' in response:
        for obj in response['Contents']:
            if file_name in obj['Key']:
                file_size = obj['Size']
                print(f"Object: {obj['Key']} - Size: {file_size:.2f} bytes")
    else:
        print(f"No objects found in {bucket_name}")

def list_buckets():
    response = s3.list_buckets()
    buckets = [bucket['Name'] for bucket in response['Buckets']]
    return buckets

def s3_search_file(file_path):
    file_name = file_path.split('/')[-1]
    buckets = list_buckets()
    for bucket in buckets:
        list_objects_with_sizes(bucket, file_name)

def dt(hour, minute=0, second=0):
    return datetime(2017, 1, 1, hour, minute, second)

def test_preprocess_orders():
    data = [
        (13450,93700,850),
        (8577,13150,126),
        (4308,13073,95),
        (3655,73252, 882),
    ]

    columns = ['seller_zip_code_prefix', 'customer_zip_code_prefix', 'delivery_distance_km']
    df_result = pd.DataFrame(data, columns=columns)
    input_file = 's3://delivery-prediction/test_batch.csv'
    output_file = 's3://delivery-prediction/predicted_batch.csv'

    save_data(df_result, input_file)

    s3_search_file(input_file)

    os.system(f'python src/predict_batch.py /srv/src/config.yml {input_file} {output_file}')

    result_df = read_data(output_file, start_dt=None, end_dt=None)

    assert result_df['prediction'].sum() == pytest.approx(893.38, abs=1e-2)

    resul_rows = df_result.shape[0]
    expected_result = 4
    assert resul_rows == expected_result
