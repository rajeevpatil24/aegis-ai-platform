import subprocess
import time
import os
import socket

# Helper: check port availability
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


print("\nStarting Aegis AI Platform...\n")

# ================================
# STEP 1: START FASTAPI
# ================================
if not is_port_in_use(8090):
    print("Starting RAG API (FastAPI) on port 8090...")
    subprocess.Popen([
        "uvicorn",
        "apps.aegis-api.app:app",
        "--host", "0.0.0.0",
        "--port", "8090"
    ])
else:
    print("FastAPI already running on 8090")

time.sleep(3)


# ================================
# STEP 2: START MLFLOW
# ================================
if not is_port_in_use(5001):
    print("Starting MLflow UI on port 5001...")
    subprocess.Popen([
        "mlflow",
        "ui",
        "--host", "0.0.0.0",
        "--port", "5001",
        "--backend-store-uri",
        "file:///Users/username/Desktop/projects/aegis-ai-platform/mlruns"
    ])
else:
    print("MLflow already running on 5001")

time.sleep(3)


# ================================
#  STEP 3: START AIRFLOW
# ================================
if not is_port_in_use(8085):
    print(" Starting Airflow on port 8085...")
    os.environ["AIRFLOW__API__PORT"] = "8085"
    subprocess.Popen(["airflow", "standalone"])
else:
    print(" Airflow already running on 8085")

time.sleep(5)


# ================================
# 🔹 STEP 4: PRINT STATUS
# ================================
print("\n Aegis Platform Ready!\n")

print(" Services Running:")
print(" RAG API        → http://localhost:8090/docs")
print(" MLflow UI      → http://localhost:5001")
print(" Airflow UI     → http://localhost:8085")

print("\n Test Commands:")

print("""
curl --get "http://localhost:8090/rag/ask" \\
  --data-urlencode "q=team collaboration"
""")

print("\n Next Steps:")
print("1. Open Airflow UI")
print("2. Enable DAG → aegis_rag_v4")
print("3. Click Trigger\n")

# ================================
#  KEEP PROCESS ALIVE
# ================================
while True:
    time.sleep(60)