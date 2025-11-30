import paho.mqtt.client as mqtt  # paho-mqtt==1.6.1
import time
import logging
import os
import csv
import json

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("mqtt-publisher")
logger.setLevel(logging.INFO)


def relative_path(rel_path):
    return os.path.join(os.path.dirname(__file__), rel_path)


def read_csv_data(file_path):
    """Reads the CSV file and returns a list of dictionaries representing the data"""
    data = []
    with open(file_path, 'r', encoding='utf-8-sig') as file:
        # Use semicolon as delimiter since the CSV uses semicolons
        csv_reader = csv.DictReader(file, delimiter=';')
        for row in csv_reader:
            # Convert numeric fields to appropriate types
            for key, value in row.items():
                if value and key != 'Vehicle Model' and key != 'Time of Day' and key != 'Day of Week':
                    try:
                        # Try to convert to float first
                        row[key] = float(value)
                    except ValueError:
                        # If conversion fails, keep as string
                        pass
            data.append(row)
    return data


ca_crt = relative_path("certs/ca.crt")
client_crt = relative_path("certs/client.crt")
client_key = relative_path("certs/client.key")

# Check if certificates exist before proceeding
cert_files = [ca_crt, client_crt, client_key]
for cert_file in cert_files:
    if not os.path.exists(cert_file):
        logger.error(f"Certificate file not found: {cert_file}")
        logger.error(
            "Please ensure TLS certificates are properly set up before running this script."
        )
        exit(1)

# Update broker hostname to match subscriber.py
broker_hostname = "localhost"
port = 8883


def on_connect(client, userdata, flags, return_code):
    if return_code == 0:
        logger.info("Connected to broker")
    else:
        logger.error(f"Could not connect, return code: {return_code}")


def format_message(row_data):
    """Format the row data into a JSON message for MQTT"""
    # Create a message with the row data including all fields
    message = {
        "timestamp": time.time(),
        "data": row_data
    }
    return json.dumps(message)


client = mqtt.Client("Publisher")
client.on_connect = on_connect

# Set username and password for authentication
client.username_pw_set("idc_user", "sec123")

client.tls_set(ca_certs=ca_crt, certfile=client_crt, keyfile=client_key)
client.tls_insecure_set(True)

try:
    logger.info("Connecting to broker...")
    client.connect(broker_hostname, port)
    client.loop_start()

    topic = "idc/ev"

    # Read the CSV data
    csv_file_path = relative_path("dataset-EV_with_stations_for_online_simulation.csv")
    csv_data = read_csv_data(csv_file_path)

    logger.info(f"Loaded {len(csv_data)} records from CSV file")

    # Publish each record at regular intervals
    for idx, record in enumerate(csv_data):
        formatted_message = format_message(record)

        result = client.publish(topic, formatted_message)
        status = result[0]
        if status == 0:
            logger.info(f"Message {idx+1}/{len(csv_data)} published: {formatted_message[:100]}...")
        else:
            logger.error(f"Failed to send message {idx+1} to topic {topic}")

        # Wait 2 seconds between messages
        time.sleep(2)

    logger.info("All messages have been published.")

finally:
    client.loop_stop()
