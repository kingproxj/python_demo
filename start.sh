#!/usr/bin/env bash

export MODEL_PKL_URI=http://10.221.128.170.xip.io:30885
export FEATURE_CSV_URI=http://10.221.128.170.xip.io:30885
export TRAIN_FILES_URI=http://10.221.128.170.xip.io:30885
export TEST_FILES_URI=http://10.221.128.170.xip.io:30885

set -x

MODEL_PKL_URI=${MODEL_PKL_URI:-localhost:8080}
FEATURE_CSV_URI=${FEATURE_CSV_URI:-localhost:8080}
TRAIN_FILES_URI=${TRAIN_FILES_URI:-localhost:8080}
TEST_FILES_URI=${TEST_FILES_URI:-localhost:8080}

mkdir -p /python_demo/model_file/loan
mkdir -p /python_demo/model_pkl/loan

#test scripts
echo "test scripts"
curl -X GET --header 'Accept: text/plain' "$FEATURE_CSV_URI/health"

#http://k8s-ids:32285/download/
echo "download features csv files from $FEATURE_CSV_URI"
curl -X GET --header 'Accept: application/octet-stream' "$FEATURE_CSV_URI/download/change_info.csv" -o /score/model_file/loan/change_info.csv
curl -X GET --header 'Accept: application/octet-stream' "$FEATURE_CSV_URI/download/company_baseinfo.csv" -o /score/model_file/loan/company_baseinfo.csv
curl -X GET --header 'Accept: application/octet-stream' "$FEATURE_CSV_URI/download/contribution.csv" -o /score/model_file/loan/contribution.csv
curl -X GET --header 'Accept: application/octet-stream' "$FEATURE_CSV_URI/download/contribution_year.csv" -o /score/model_file/loan/contribution_year.csv
curl -X GET --header 'Accept: application/octet-stream' "$FEATURE_CSV_URI/download/enterprise_baseinfo.csv" -o /score/model_file/loan/enterprise_baseinfo.csv
curl -X GET --header 'Accept: application/octet-stream' "$FEATURE_CSV_URI/download/enterprise_social_security.csv" -o /score/model_file/loan/enterprise_social_security.csv

echo "download models from $MODEL_PKL_URI"
curl -X GET --header 'Accept: application/octet-stream' "$MODEL_PKL_URI/download/dump_raw_etc.pkl" -o /score/model_pkl/loan/dump_raw_etc.pkl
curl -X GET --header 'Accept: application/octet-stream' "$MODEL_PKL_URI/download/dump_raw_gbc.pkl" -o /score/model_pkl/loan/dump_raw_gbc.pkl
curl -X GET --header 'Accept: application/octet-stream' "$MODEL_PKL_URI/download/dump_raw_xgb.pkl" -o /score/model_pkl/loan/dump_raw_xgb.pkl
curl -X GET --header 'Accept: application/octet-stream' "$MODEL_PKL_URI/download/Ridge_Blend.pkl" -o /score/model_pkl/loan/Ridge_Blend.pkl

echo "download train model and csv from $TRAIN_FILES_URI"
curl -X GET --header 'Accept: application/octet-stream' "$TRAIN_FILES_URI/download/jinan_good_bad_data_all.csv" -o /score/model_file/loan/jinan_good_bad_data_all.csv
curl -X GET --header 'Accept: application/octet-stream' "$TRAIN_FILES_URI/download/jinan_good_bad_data_all.pkl" -o /score/model_file/loan/jinan_good_bad_data_all.pkl
curl -X GET --header 'Accept: application/octet-stream' "$FEATURE_CSV_URI/download/train_x.pkl" -o /score/model_file/loan/train_x.pkl

echo "download test model and csv from $TEST_FILES_URI"
curl -X GET --header 'Accept: application/octet-stream' "$FEATURE_CSV_URI/download/test_x.pkl" -o /score/model_file/loan/test_x.pkl

#uwsgi --http :8080 --wsgi-file score_server.py
