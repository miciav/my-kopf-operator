FROM python:3.10-slim

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["kopf", "run", "--all-namespaces", "/usr/src/app/operator/main.py"]
