#!/bin/bash

echo " Cleaning Aegis AI Platform..."

# ================================
#  1. Kill Local Processes
# ================================

echo " Killing local services..."

ports=(8090 5001 8085)

for port in "${ports[@]}"
do
  pid=$(lsof -ti :$port)
  if [ ! -z "$pid" ]; then
    echo "Killing process on port $port (PID: $pid)"
    kill -9 $pid
  else
    echo "No process running on port $port"
  fi
done

# Kill airflow processes
pkill -f airflow || true
pkill -f uvicorn || true
pkill -f mlflow || true

echo " Local processes stopped"


# ================================
#  2. Terraform Destroy (AWS)
# ================================

echo " Destroying AWS infrastructure..."

cd terraform || exit

terraform init

terraform destroy -auto-approve

cd ..

echo " AWS resources destroyed"


# ================================
#  3. Optional: Clean MLflow data
# ================================

echo " Cleaning MLflow local data..."

rm -rf mlruns || true

echo " Cleanup complete"

# shellcheck disable=SC2046
docker stop $(docker ps -q) 2>/dev/null || true
docker system prune -af || true