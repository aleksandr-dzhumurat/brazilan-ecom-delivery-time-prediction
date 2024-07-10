import os
import sys
import zipfile

import pandas as pd
import numpy as np

from utils import get_config, filter_df_by_date

def extract_zip(root_dataset_dir):
    zip_file_path = os.path.join(root_dataset_dir, 'brazilian_eommerce.zip')
    extraction_dir = os.path.join(root_dataset_dir, 'brazilian_eommerce')

    if not os.path.exists(extraction_dir):
        os.makedirs(extraction_dir)

    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(extraction_dir)

    print(f'All files have been extracted to {extraction_dir}')

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius in kilometers
    lat1_rad, lon1_rad, lat2_rad, lon2_rad = map(np.radians, [lat1, lon1, lat2, lon2])

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = np.sin(dlat / 2.0)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2.0)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    distance = R * c
    return distance

def preprocess_orders(df, filter_threshold=None):
    df['delivery_time'] = (
        (
            pd.to_datetime(df['order_delivered_customer_date']) -
            pd.to_datetime(df['order_purchase_timestamp'])
        )
        .apply(lambda td: td.total_seconds() / (60*60))
    )
    if filter_threshold is None:
        filter_threshold = df['delivery_time'].quantile(0.95)
    df = df[df['delivery_time'] <= filter_threshold]
    return df


def prepare_data(root_dir, start_date, end_date):
    result_csv_path = os.path.join(root_dir, 'merged_dataset.csv')
    root_data_dir = os.path.join(root_dir, 'dataset', 'brazilian_eommerce')
    if os.path.exists(result_csv_path):
        return result_csv_path

    orders_dataset = pd.read_csv(os.path.join(root_data_dir, 'olist_orders_dataset.csv'))
    orders_dataset['purchase_dt'] = pd.to_datetime(orders_dataset['order_purchase_timestamp'].apply(lambda x: x[:10]))

    orders_filtered_df = filter_df_by_date(
        orders_dataset, dt_col='order_purchase_timestamp',
        date_filter={'start_date': start_date, 'end_date': end_date}
    )
    orders_filtered_df = preprocess_orders(orders_filtered_df)
    #
    sellers_df = pd.read_csv(os.path.join(root_data_dir, 'olist_sellers_dataset.csv'))
    customers_df = pd.read_csv(os.path.join(root_data_dir, 'olist_customers_dataset.csv'))
    locations_df = pd.read_csv(os.path.join(root_data_dir, 'olist_geolocation_dataset.csv'))
    orders_items_dataset = pd.read_csv(os.path.join(root_data_dir, 'olist_order_items_dataset.csv'))
    # because of zip_code_prefix != zip_code, so we need deduplicate data
    locations_df = (
        locations_df
        .groupby('geolocation_zip_code_prefix')[['geolocation_lat', 'geolocation_lng']]
        .mean()
        .reset_index()
    )

    delivery_df = (
        orders_filtered_df[['order_id', 'purchase_dt', 'customer_id', 'order_delivered_customer_date', 'order_purchase_timestamp', 'delivery_time']]
        .merge(orders_items_dataset[['order_id', 'price', 'seller_id', 'product_id']], on='order_id')
        .merge(sellers_df[['seller_id', 'seller_zip_code_prefix']], on='seller_id')
        .merge(customers_df[['customer_id', 'customer_zip_code_prefix']], on='customer_id')
        .merge(
            locations_df[['geolocation_zip_code_prefix', 'geolocation_lat', 'geolocation_lng']]
                .rename(columns={'geolocation_zip_code_prefix': 'customer_zip_code_prefix', 'geolocation_lat': 'dest_lat', 'geolocation_lng': 'dest_lng'}),
            on='customer_zip_code_prefix'
        )
        .merge(
            locations_df[['geolocation_zip_code_prefix', 'geolocation_lat', 'geolocation_lng']]
                .rename(columns={'geolocation_zip_code_prefix': 'seller_zip_code_prefix', 'geolocation_lat': 'start_lat', 'geolocation_lng': 'start_lng'}),
            on='seller_zip_code_prefix'
        )
    )
    delivery_df['delivery_distance_km'] = delivery_df.apply(lambda row: haversine(row['start_lat'], row['start_lng'], row['dest_lat'], row['dest_lng']), axis=1)

    delivery_df.to_csv(result_csv_path, index=False)
    return result_csv_path

def prepare_train_test(input_csv_path, config):
    train_csv_path = os.path.join(config['root_data_dir'], 'train_dataset.csv')
    valid_csv_path = os.path.join(config['root_data_dir'], 'valid_dataset.csv')
    if os.path.exists(train_csv_path) and os.path.exists(valid_csv_path):
        return
    df = pd.read_csv(input_csv_path)
    dt_col = 'purchase_dt'

    date_start = config['data_params']['train_date_start']
    date_end = config['data_params']['train_date_end']

    mask = (df[dt_col] >= date_start) | (df[dt_col] <= date_end)
    df[mask].to_csv(train_csv_path, index=False)

    date_start = config['data_params']['valid_date_start']
    date_end = config['data_params']['valid_date_end']
    mask = (df[dt_col] >= date_start) | (df[dt_col] >= date_end)
    df[mask].to_csv(valid_csv_path, index=False)
    print('Train test split complited')

if __name__ == '__main__':
    config = get_config(sys.argv[1])
    dataset_dir = os.path.join(config['root_data_dir'], 'dataset')

    extract_zip(dataset_dir)

    date_start = config['data_params']['date_start']
    date_end = config['data_params']['date_end']
    result_csv_path = prepare_data(config['root_data_dir'], date_start, date_end)

    prepare_train_test(result_csv_path, config=config)