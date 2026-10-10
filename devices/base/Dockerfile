FROM debian:13

RUN apt-get update && apt-get install -y \
    openssh-server \
    sudo \
    iproute2 \
    iptables \
    iputils-ping \
    traceroute \
    curl \
    dnsutils \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -s /bin/bash admin && \
    echo "admin:admin" | chpasswd && \
    echo "admin ALL=(ALL) NOPASSWD: ALL" \
        > /etc/sudoers.d/admin && \
    chmod 440 /etc/sudoers.d/admin

RUN mkdir -p /run/sshd

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

CMD ["tail", "-f", "/dev/null"]
