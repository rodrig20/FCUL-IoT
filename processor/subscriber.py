import paho.mqtt.client as mqtt
import logging


__logger = logging.getLogger("mqtt-subscriber")
__logger.setLevel(logging.INFO)


def start_mqtt_client():
    """Initializes the MQTT client and starts a blocking loop"""

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
    port = 1883

    client = mqtt.Client("Processor")
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        __logger.info("Connecting to broker...")
        client.connect(broker_hostname, port)
        client.loop_start()

        return client
    except Exception as e:
        __logger.error(f"Error connecting or starting loop: {e}")
