# Integração IoT: Home Assistant + MQTT + MQTT-SN

Projeto prático desenvolvido para demonstrar a integração de dispositivos IoT de baixo consumo ao **Home Assistant**, utilizando uma ponte entre os protocolos **MQTT-SN** (via UDP) e **MQTT tradicional** (via TCP).

Todo o ambiente roda isolado em contêineres Docker orquestrados pelo Docker Compose.

```

### O que faz cada componente:

1. **Publisher MQTT-SN (`publisher-mqttsn`)**: Script em Python que simula um sensor físico de temperatura e umidade. Envia leituras periódicas usando datagramas UDP puros no formato da especificação MQTT-SN v1.2.
2. **Gateway MQTT-SN (`gateway-mqttsn`)**: Baseado no código oficial em C++ do *Eclipse Paho*. Ele escuta na porta UDP `10000`, recebe os pacotes do sensor, converte os Topic IDs em tópicos textuais e repassa para o Mosquitto via TCP.
3. **Broker MQTT (`mosquitto`)**: Instância do *Eclipse Mosquitto 2.x* na porta TCP `1883`. Recebe do Gateway e redistribui para os clientes inscritos.
4. **Subscriber MQTT (`subscriber-mqtt`)**: Cliente Python que se inscreve no tópico `sensores/#` e joga no terminal as mensagens que chegam no broker, servindo para auditoria e teste de entrega.
5. **Home Assistant (`homeassistant`)**: Servidor de automação que consome os dados do Mosquitto e plota as leituras nos painéis e gráficos de histórico.

---

## 📂 Estrutura de Arquivos

```text
├── compose.yaml                      # Sobe os 5 contêineres na rede 'iot-net'
├── README.md                         # Este guia
├── .gitignore
├── mosquitto/
│   └── config/
│       └── mosquitto.conf            # Permite conexões anônimas na porta 1883
├── gateway-mqttsn/
│   ├── Dockerfile                    # Compila o Paho Gateway C++ com CMake e OpenSSL
│   └── gateway.conf                  # Aponta para o broker 'mosquitto:1883'
├── publisher-mqttsn/
│   ├── Dockerfile
│   └── publisher.py                  # Sensor simulado (sockets UDP)
├── subscriber-mqtt/
│   ├── Dockerfile
│   ├── requirements.txt              # paho-mqtt
│   └── subscriber.py                 # Logger das mensagens
└── homeassistant/
    ├── configuration.yaml            # Configuração manual dos sensores MQTT
    ├── automations.yaml
    ├── scripts.yaml
    └── scenes.yaml
```

---

<<<<<<< HEAD
## 🚀 Como Executar em Sala de Aula
=======
## 3. Pré-requisitos (Na Máquina Ubuntu)

Em uma máquina com **Ubuntu 22.04 ou superior** (em VM VMware, VirtualBox ou WSL2), abra o terminal e execute:
>>>>>>> 512103eedad55daa84decf34f7401843c605134f

### 1. Pré-requisitos
Ter o **Docker** e o **Docker Compose** instalados (testado no Ubuntu 22.04 / 24.04):
```bash
sudo apt update
sudo apt install -y docker.io docker-compose-v2 git
sudo usermod -aG docker $USER
newgrp docker
```

### 2. Clonar e subir o ambiente
```bash
git clone https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git home-assistant-iot
cd home-assistant-iot
docker compose up -d --build
```
*(No primeiro build, o Docker vai baixar as imagens e compilar o código C++ do Gateway. Isso leva cerca de 1 a 2 minutos).*

### 3. Conferir se tudo subiu
```bash
docker compose ps
```
Todos os 5 serviços devem aparecer com status **`Up`**.

### 4. Ver as mensagens chegando no terminal
Para acompanhar o fluxo de dados em tempo real:
```bash
docker compose logs -f subscriber-mqtt
```
Você verá as mensagens formatadas de temperatura e umidade caindo a cada 5 segundos. Use `Ctrl + C` para sair dos logs.

---

## 🖥️ Configuração no Home Assistant

1. No navegador, abra: `http://localhost:8123` (ou `http://<IP-DA-VM>:8123`).
2. Conclua o cadastro inicial de usuário/senha de administrador.
3. Vá em **Configurações** $\rightarrow$ **Dispositivos e Serviços**.
4. Clique em **Adicionar Integração**, pesquise por **MQTT** e preencha:
   * **Broker:** `mosquitto`
   * **Porta:** `1883`
   * **Usuário / Senha:** *(deixar em branco)*
   * Clique em **Enviar**.
5. Vá na aba **Histórico** (no menu lateral) e busque por `Temperatura Sala (MQTT-SN)` para visualizar a linha do gráfico variando com as leituras do sensor.
6. Na tela inicial (**Visão Geral**), os valores de temperatura e umidade já estarão disponíveis em **Favoritos**.

---

## ⚙️ Detalhes Importantes de Implementação

Durante o desenvolvimento do laboratório, dois pontos técnicos foram fundamentais para o funcionamento correto:

* **Regra do `MsgId` no MQTT-SN (QoS 0):** Pela norma MQTT-SN v1.2, mensagens publicadas com `QoS = 0` devem obrigatoriamente ter o campo `MsgId` preenchido com `0x0000`. Usar qualquer valor diferente faz o Gateway rejeitar os pacotes silenciosamente com `Invalid MsgId`. Isso já está tratado no `publisher.py`.
* **Compilação do Gateway Paho:** O repositório atual da Eclipse Foundation compila o gateway usando CMake (`./build.sh udp`) e depende de `libssl-dev`. Por isso, o Dockerfile foi montado sobre `debian:bookworm-slim`, evitando problemas de compatibilidade com a biblioteca `glibc`.
* **Portas de Rede:** O MQTT-SN roda sobre **UDP** na porta `10000`, enquanto o MQTT tradicional roda sobre **TCP** na porta `1883`.

---

## 🛑 Como Parar o Ambiente

Para pausar os contêineres mantendo os dados salvos:
```bash
docker compose stop
```

Para remover os contêineres e a rede:
```bash
docker compose down
```
