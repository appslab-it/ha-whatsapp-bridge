ARG BUILD_FROM=devlikeapro/waha:latest
FROM ${BUILD_FROM}

# Install jq for parsing Home Assistant options
RUN apt-get update && \
    apt-get install -y --no-install-recommends jq curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy startup script
COPY rootfs/run.sh /run.sh
RUN chmod +x /run.sh

WORKDIR /app

CMD ["/run.sh"]
