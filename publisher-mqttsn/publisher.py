import os
import sys
import time
import socket
import struct
import random
import datetime

GATEWAY_HOST = os.getenv("GATEWAY_HOST", "gateway-mqttsn")
GATEWAY_PORT = int(os.getenv("GATEWAY_PORT", "10000"))
CLIENT_ID = os.getenv("CLIENT_ID", "Sensor-SN-01")
INTERVAL = int(os.getenv("PUBLISH_INTERVAL", "5"))

TYPE_CONNECT    = 0x04
TYPE_CONNACK    = 0x05
TYPE_REGISTER   = 0x0A
TYPE_REGACK     = 0x0B
TYPE_PUBLISH    = 0x0C

class MQTTSNClient:
    def __init__(self, host, port, client_id):
        self.host = host
        self.port = port
        self.client_id = client_id
        self.sock = None
        self.msg_id = 1
        self.topics = {}

    def _next_msg_id(self):
        mid = self.msg_id
        self.msg_id = (self.msg_id + 1) & 0xFFFF
        if self.msg_id == 0:
            self.msg_id = 1
        return mid

    def connect_socket(self):
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(5.0)

    def send_packet(self, packet):
        self.sock.sendto(packet, (self.host, self.port))

    def recv_packet(self):
        try:
            data, _ = self.sock.recvfrom(2048)
            return data
        except socket.timeout:
            return None

    def connect(self):
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [MQTT-SN-PUB] Conectando ao Gateway {self.host}:{self.port} (UDP)...")
        self.connect_socket()

        client_bytes = self.client_id.encode('utf-8')
        length = 6 + len(client_bytes)
        duration = 300
        packet = struct.pack(f'!BBBBH{len(client_bytes)}s',
                             length, TYPE_CONNECT, 0x04, 0x01, duration, client_bytes)

        for attempt in range(1, 10):
            try:
                self.send_packet(packet)
                resp = self.recv_packet()
                if resp and len(resp) >= 3 and resp[1] == TYPE_CONNACK:
                    if resp[2] == 0:
                        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [MQTT-SN-PUB] Conexao aceita pelo Gateway (CONNACK = 0x00)!")
                        return True
            except Exception:
                pass
            time.sleep(2)
        return False

    def register_topic(self, topic_name):
        t_bytes = topic_name.encode('utf-8')
        mid = self._next_msg_id()
        length = 6 + len(t_bytes)
        packet = struct.pack(f'!BBHH{len(t_bytes)}s',
                             length, TYPE_REGISTER, 0x0000, mid, t_bytes)

        for _ in range(5):
            self.send_packet(packet)
            resp = self.recv_packet()
            if resp and len(resp) >= 7 and resp[1] == TYPE_REGACK:
                _, _, assigned_topic_id, _, ret_code = struct.unpack('!BBHHB', resp[:7])
                if ret_code == 0:
                    self.topics[topic_name] = assigned_topic_id
                    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [MQTT-SN-PUB] Topico '{topic_name}' registrado com ID {assigned_topic_id}")
                    return assigned_topic_id
            time.sleep(1)
        return None

    def publish(self, topic_id, payload_str):
        p_bytes = payload_str.encode('utf-8')
        length = 7 + len(p_bytes)
        # Pela especificacao MQTT-SN v1.2: em mensagens com QoS 0, MsgId DEVE ser obrigatoriamente 0x0000!
        mid = 0x0000
        flags = 0x00 # QoS 0, TopicIdType = normal
        packet = struct.pack(f'!BBBHH{len(p_bytes)}s',
                             length, TYPE_PUBLISH, flags, topic_id, mid, p_bytes)
        self.send_packet(packet)

def main():
    time.sleep(3)
    client = MQTTSNClient(GATEWAY_HOST, GATEWAY_PORT, CLIENT_ID)

    while True:
        try:
            if not client.connect():
                time.sleep(5)
                continue

            id_temp = client.register_topic("sensores/temperatura")
            id_hum  = client.register_topic("sensores/umidade")

            if id_temp is None or id_hum is None:
                time.sleep(5)
                continue

            temp_base, hum_base = 23.5, 55.0
            while True:
                temp = round(temp_base + random.uniform(-1.5, 1.5), 1)
                hum  = round(hum_base + random.uniform(-4.0, 4.0), 1)

                print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [MQTT-SN-PUB] Publicando Temp={temp}°C | Hum={hum}%")
                client.publish(id_temp, f"{temp}")
                client.publish(id_hum, f"{hum}")
                time.sleep(INTERVAL)

        except Exception as e:
            time.sleep(5)

if __name__ == "__main__":
    main()
