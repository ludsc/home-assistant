import os
import sys
import time
import datetime
import paho.mqtt.client as mqtt

BROKER_HOST = os.getenv("BROKER_HOST", "mosquitto")
BROKER_PORT = int(os.getenv("BROKER_PORT", "1883"))
TOPIC = os.getenv("SUBSCRIBE_TOPIC", "sensores/#")

def on_connect(client, userdata, flags, rc, *args):
    if rc == 0:
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [MQTT-SUB] Conectado ao broker MQTT ({BROKER_HOST}:{BROKER_PORT}) com sucesso!")
        client.subscribe(TOPIC)
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [MQTT-SUB] Inscrito no topico: '{TOPIC}'")
    else:
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [MQTT-SUB] Falha na conexao. Codigo de retorno: {rc}")

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode('utf-8', errors='replace')
    except Exception:
        payload = str(msg.payload)
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print("=" * 60)
    print(f"[{timestamp}] MENSAGEM RECEBIDA VIA BROKER MQTT:")
    print(f"  Topico:  {msg.topic}")
    print(f"  QoS:     {msg.qos}")
    print(f"  Payload: {payload}")
    print("=" * 60, flush=True)

def main():
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [MQTT-SUB] Iniciando Subscriber MQTT...")
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [MQTT-SUB] Alvo: {BROKER_HOST}:{BROKER_PORT}")
    
    # Compatibilidade com versoes 1.x e 2.x do paho-mqtt
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id="mqtt-subscriber-logger")
    except AttributeError:
        client = mqtt.Client(client_id="mqtt-subscriber-logger")

    client.on_connect = on_connect
    client.on_message = on_message

    # Loop de conexao com retentativa
    while True:
        try:
            print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [MQTT-SUB] Tentando conectar ao broker...")
            client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
            break
        except Exception as e:
            print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [MQTT-SUB] Broker indisponivel ({e}). Aguardando 3s...")
            time.sleep(3)

    client.loop_forever()

if __name__ == "__main__":
    main()
