FROM lab-base

RUN apt-get update && \
    apt-get install -y bind9 bind9-utils dnsutils && \
    rm -rf /var/lib/apt/lists/*

CMD ["named", "-g", "-c", "/etc/bind/named.conf"]
