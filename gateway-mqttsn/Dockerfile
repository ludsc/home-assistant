# ==============================================================================
# Dockerfile para Eclipse Paho MQTT-SN Gateway (C++)
# ==============================================================================

FROM debian:bookworm-slim

# Instala todas as ferramentas de compilacao e bibliotecas necessarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    libssl-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN git clone https://github.com/eclipse/paho.mqtt-sn.embedded-c.git

WORKDIR /app/paho.mqtt-sn.embedded-c

# Compila o MQTTSNGateway nativamente
RUN mkdir -p build && cd build && \
    cmake .. -DSENSORNET=udp && \
    make MQTT-SNGateway && \
    cp /app/paho.mqtt-sn.embedded-c/MQTTSNGateway/bin/MQTT-SNGateway /app/MQTT-SNGateway

WORKDIR /app
COPY gateway.conf /app/gateway.conf

EXPOSE 10000/udp

ENTRYPOINT ["/app/MQTT-SNGateway", "-f", "/app/gateway.conf"]
