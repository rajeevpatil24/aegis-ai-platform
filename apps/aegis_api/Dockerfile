FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install rebuff

COPY . .
ENV LANGFUSE_PUBLIC_KEY=pk-XXXXXXXXXXXXXXXXXXXXXXX
ENV LANGFUSE_SECRET_KEY=sk-XXXXXXXXXXXXXXXXXXXXXXX
ENV LANGFUSE_HOST=http://host.docker.internal:3005


CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]