# Projeto FCUL IoT

Um projeto abrangente de IoT que implementa comunicação baseada em MQTT com uma interface de dashboard para visualização de dados e futura integração de modelos de machine learning.

## Utilização

### Iniciar o Sistema
```bash
docker-compose up -d
```

### Pré-requisitos

- Docker
- Docker Compose
- Python 3.8+ (para testar o broker)

### Testar a Arquitetura
Pode testar se a arquitetura está a funcionar executando o utilitário publisher:
```bash
# Precisa de paho-mqtt==1.6.1
python utils/publisher.py
```

Isto irá publicar mensagens de teste com diferentes modelos de previsão iris no broker MQTT.

### Parar o Sistema

Sem apagar a base de dados:
```bash
docker-compose down
```

Apagando a base de dados
```bash
docker-compose down -v
```

## Instruções de Configuração

1. Clone o repositório:
   ```bash
   git clone https://github.com/rodrig20/FCUL-IoT.git
   cd FCUL-IoT
   ```

2. Crie o ficheiro .env com as variáveis necessárias:
   ```bash
   # Crie o ficheiro .env baseado no exemplo (se existir)
   cp .env_example .env # se .env_example existir
   # Caso contrário, crie manualmente
   ```

3. Defina as variáveis de ambiente necessárias no ficheiro .env (ver secção abaixo)

### Variáveis de Ambiente

O ficheiro `.env` deve conter as seguintes variáveis de ambiente:

```bash
DB_USER=<YourUsername>
DB_PASSWORD=<YourPassword>
DB_DB=<YourDatabase>
```


## Arquitetura

O projeto consiste em múltiplos componentes:

- **Mosquitto MQTT Broker**: Lida com a comunicação MQTT entre componentes
- **Dashboard**: Interface web para visualização de dados
- **Processor**: Processa dados recebidos do broker MQTT e faz a ponte entre o dashboard e a Base de Dados
- **Base de Dados**: Armazena os dados processados pelo Processor com PostregreSQL
- **Utils**: Scripts auxiliares para testes da estrutura

### Mosquitto MQTT Broker

- Configuração: `mosquitto/mosquitto.conf`
- Registos são armazenados em `mosquitto/log/`
- Dados são armazenados em `mosquitto/data/`

### Dashboard

- Interface web para visualização
- Conecta ao broker MQTT para receber dados em tempo real

### Processor

- Processa mensagens MQTT recebidas
- Serve como ponte entre o Dashboard e a Base de Dados

### Base de Dados

- Armazena os dados processados pelo Processor
- Integração com o sistema para persistência de dados

### Utils

- `utils/publisher.py`: Publica mensagens de teste nos tópicos MQTT.


## Contribuição

1. Crie uma branch no repositório atual
2. Faça as suas alterações
3. Commit e push
4. Crie um pull request
