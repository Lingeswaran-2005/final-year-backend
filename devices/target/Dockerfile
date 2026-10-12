FROM lab-base

RUN apt-get update && \
    apt-get install -y python3 && \
    rm -rf /var/lib/apt/lists/*

    
COPY routes.sh /usr/local/bin/routes.sh
RUN chmod +x /usr/local/bin/routes.sh


CMD ["/usr/local/bin/routes.sh"]
