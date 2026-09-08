FROM debian:13

RUN apt-get update && \
    apt-get install -y \
        openssh-server \
        sudo \
        iptables \
        curl \
        traceroute \
        dnsutils \
        iputils-ping \
        iproute2 \
        net-tools \
        python3 && \
    rm -rf /var/lib/apt/lists/*

# Create admin user
RUN useradd -m -s /bin/bash admin && \
    echo "admin:admin" | chpasswd && \
    echo "admin ALL=(ALL) NOPASSWD: ALL" \
        > /etc/sudoers.d/admin && \
    chmod 440 /etc/sudoers.d/admin

# SSH runtime directory
RUN mkdir -p /run/sshd

# Start SSH server and keep container running
CMD ["/bin/bash", "-c", "/usr/sbin/sshd && tail -f /dev/null"]