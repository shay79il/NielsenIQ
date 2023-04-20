# NielsenIQ

## Prerequisits:
### 1. `Docker` and `docker-compose` installed

### 2. Set the following env variables
```bash
AIRFLOW_IMAGE_NAME="apache/airflow:2.5.1"
AIRFLOW_UID=
AIRFLOW_PROJ_DIR=
```

### 3. Run the following cli command
```bash
curl -X POST \
     -H "Content-Type: application/json" \
     -d '{"conf": {"environment_type": "production"}}' \
     --user "airflow:airflow" \
     http://localhost:8080/api/v1/dags/example_dag/dagRuns
```