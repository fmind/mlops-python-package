# run mlflow tasks
[group('mlflow')]
mlflow: mlflow-doctor mlflow-serve

# run mlflow doctor
[group('mlflow')]
mlflow-doctor:
    uv run mlflow doctor

# start mlflow server
[group('mlflow')]
mlflow-serve host="127.0.0.1" port="5000" uri="./mlruns":
    uv run mlflow server --host={{host}} --port={{port}} --backend-store-uri={{uri}}
