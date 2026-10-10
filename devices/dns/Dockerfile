FROM lab-base

RUN apt-get update && \
    apt-get install -y bind9 bind9-utils dnsutils && \
    mkdir -p /etc/bind/zones && \
    rm -rf /var/lib/apt/lists/*

COPY named.conf.local /etc/bind/named.conf.local
COPY zones/db.lab.test /etc/bind/zones/db.lab.test

COPY routes.sh /usr/local/bin/routes.sh
RUN chmod +x /usr/local/bin/routes.sh

ENTRYPOINT ["/usr/local/bin/routes.sh"]

CMD ["named", "-g", "-c", "/etc/bind/named.conf"]
