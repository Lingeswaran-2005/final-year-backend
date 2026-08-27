FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    traceroute \
    dnsutils \
    iputils-ping \
    iproute2 \
    net-tools \
    openssh-client

COPY requirements.txt .

RUN pip install  --no-cache-dir -r requirements.txt

COPY src ./src

CMD ["uvicorn", "src.main:api", "--host", "0.0.0.0", "--port", "8000"]