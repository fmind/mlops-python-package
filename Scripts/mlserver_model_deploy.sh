export MLFLOW_TRACKING_URI=http://localhost:5001
source .venv/bin/activate
mlflow models serve -m models:/model_name/1 -p 5010 --enable-mlserver
