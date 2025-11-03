import os
import logging
from subscriber import start_mqtt_client
from database import Database
from app import app


# Configure logging for the main module
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
__logger = logging.getLogger("processor-main")
__logger.setLevel(logging.INFO)


__logger.info("Starting processor application...")

# Start MQTT client
mqtt_client = start_mqtt_client()
if mqtt_client:
    __logger.info("MQTT client started successfully")
else:
    __logger.error("Failed to start MQTT client")

# Initialize the database
try:
    Database.init_db()
    __logger.info("Database initialized successfully")
except Exception as e:
    __logger.error(f"Error initializing database: {e}")

__logger.info("Processor application started")
