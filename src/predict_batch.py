"""
docker exec -it 711cba360a17  \
    python3 src/predict_batch.py /srv/src/config.yml "2027-02-01" "2017-02-02" /srv/data/train_dataset.csv /srv/data/res.csv
"""
import os
import sys

from utils import read_data, get_config, get_features, get_model, save_data

if __name__ == '__main__':

    config = get_config(sys.argv[1])

    params = config['catboost_params']
    model_path = os.path.join('/srv/data', 'model.pkl')
    model = get_model(params)
    model.load_model(model_path)

    # start_dt = sys.argv[2]
    # end_dt = sys.argv[3]

    data_path = sys.argv[2]
    output_data_path = sys.argv[3]

    df = read_data(data_path, start_dt=None, end_dt=None)
    X, _ = get_features(df)
    y_pred = model.predict(X)	    # batch_prediction_backfill(start_date, end_date)
    X['prediction'] = y_pred
    save_data(X, output_data_path)
    