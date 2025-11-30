import paho.mqtt.client as mqtt
import logging
import os
import json
from database import Database


__logger = logging.getLogger("mqtt-subscriber")
__logger.setLevel(logging.INFO)


def relative_path(rel_path):
    return os.path.join(os.path.dirname(__file__), rel_path)


def start_mqtt_client():
    """Initializes the MQTT client and starts a blocking loop"""
    ca_crt = relative_path("certs/ca.crt")
    client_crt = relative_path("certs/client.crt")
    client_key = relative_path("certs/client.key")

    # Check if certificates exist before proceeding
    cert_files = [ca_crt, client_crt, client_key]
    for cert_file in cert_files:
        if not os.path.exists(cert_file):
            __logger.error(f"Certificate file not found: {cert_file}")
            __logger.error(
                "Please ensure TLS certificates are properly set up before running this script."
            )
            return None

    def on_connect(client, userdata, flags, return_code):
        if return_code == 0:
            __logger.info("Connected to broker")
            client.subscribe("idc/ev")
        else:
            __logger.error(f"Could not connect, return code: {return_code}")

    def on_message(client, userdata, message):
        payload = message.payload.decode("utf-8")
        __logger.info(f"Received message: {payload[:150]}...") # Log a snippet

        try:
            message_dict = json.loads(payload)
            ev_data = message_dict.get("data")

            if ev_data and isinstance(ev_data, dict):
                # Call the class method to insert the data
                Database.insert_ev_data(ev_data)
            else:
                __logger.warning("No 'data' field found in message or it's not a dictionary.")

        except json.JSONDecodeError:
            __logger.error(f"Failed to decode JSON from message: {payload}")
        except Exception as e:
            __logger.error(f"An error occurred while processing message: {e}")

    broker_hostname = "mosquitto"
    port = 8883

    client = mqtt.Client("Processor")
    client.on_connect = on_connect
    client.on_message = on_message

    # Set username and password for authentication
    client.username_pw_set("idc_user", "sec123")

    try:
        __logger.info("Connecting to broker...")
        client.tls_set(ca_certs=ca_crt, certfile=client_crt, keyfile=client_key)
        client.tls_insecure_set(True)
        client.connect(broker_hostname, port)
        client.loop_start()

        return client
    except Exception as e:
        __logger.error(f"Error connecting or starting loop: {e}")
