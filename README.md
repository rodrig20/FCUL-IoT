# FCUL IoT Project

A comprehensive IoT project that implements MQTT-based communication with a dashboard interface for data visualization and future integration of machine learning models.

## Usage

### Start the System
```bash
docker compose up -d
```

### Prerequisites

- Docker
- Docker Compose
- Python 3.8+ (for testing the broker)

### Test the Architecture
You can test if the architecture is working by running the publisher utility:
```bash
# Requires paho-mqtt==1.6.1
python utils/publisher.py
```

This will publish test messages with different iris prediction models to the MQTT broker.

### Stop the System

Without deleting the database:
```bash
docker compose down
```

Deleting the database
```bash
docker compose down -v
```

## Configuration Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/rodrig20/FCUL-IoT.git
   cd FCUL-IoT
   ```

2. Create the .env file with the necessary variables:
   ```bash
   # Create the .env file based on the example (if it exists)
   cp .env_example .env # if .env_example exists
   # Otherwise, create it manually
   ```

3. Set the required environment variables in the .env file (see section below)

### Environment Variables

The `.env` file should contain the following environment variables:

```bash
DB_USER=<YourUsername>
DB_PASSWORD=<YourPassword>
DB_NAME=<YourDatabase>
```


## Architecture

The project consists of multiple components:

- **Mosquitto MQTT Broker**: Handles MQTT communication between components
- **Dashboard**: Web interface for data visualization
- **Processor**: Processes data received from the MQTT broker and acts as a bridge between the dashboard and the Database
- **Database**: Stores data processed by the Processor with PostgreSQL
- **Utils**: Helper scripts for testing the architecture

### Mosquitto MQTT Broker

- Configuration: `mosquitto/mosquitto.conf`
- Logs are stored in `mosquitto/log/`
- Data is stored in `mosquitto/data/`

### Dashboard

- Web interface for visualization
- Connects to MQTT broker to receive real-time data

### Processor

- Processes received MQTT messages
- Acts as a bridge between the Dashboard and the Database

### Database

- Stores data processed by the Processor
- Integration with the system for data persistence

### Utils

- `utils/publisher.py`: Publishes test messages to MQTT topics.


## Contribution

1. Create a branch in the current repository
2. Make your changes
3. Commit and push
4. Create a pull request
