FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    traceroute \
    dnsutils \
    iputils-ping \
    iproute2 \
    net-tools \
    openssh-client \
    iptables

COPY requirements.txt .

RUN pip install  --no-cache-dir -r requirements.txt

COPY src ./src

COPY routes.sh /usr/local/bin/routes.sh
RUN chmod +x /usr/local/bin/routes.sh

ENTRYPOINT ["/usr/local/bin/routes.sh"]

CMD ["uvicorn", "src.main:api", "--host", "0.0.0.0", "--port", "8000"]