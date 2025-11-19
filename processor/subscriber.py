import paho.mqtt.client as mqtt
import logging
import os


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
            client.subscribe("idc/iris")
        else:
            __logger.error(f"Could not connect, return code: {return_code}")

    def on_message(client, userdata, message):
        payload = str(message.payload.decode("utf-8"))
        __logger.info(f"Received message: {payload}")

        # TODO: when I know what to do, add DB-related stuff here

    broker_hostname = "mosquitto"
    port = 8883

    client = mqtt.Client("Processor")
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        __logger.info("Connecting to broker...")
        client.tls_set(ca_certs=ca_crt, certfile=client_crt, keyfile=client_key)
        client.tls_insecure_set(True)
        client.connect(broker_hostname, port)
        client.loop_start()

        return client
    except Exception as e:
        __logger.error(f"Error connecting or starting loop: {e}")
