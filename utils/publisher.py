import paho.mqtt.client as mqtt  # paho-mqtt==1.6.1
import time
import logging
import os

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("mqtt-publisher")
logger.setLevel(logging.INFO)


def relative_path(rel_path):
    return os.path.join(os.path.dirname(__file__), rel_path)


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

broker_hostname = "127.0.0.1"
port = 8883


def on_connect(client, userdata, flags, return_code):
    if return_code == 0:
        print("connected")
    else:
        print("could not connect, return code:", return_code)


client = mqtt.Client("Client1")
# client.username_pw_set(username="user_name", password="password") # uncomment if you use password auth
client.on_connect = on_connect

client.tls_set(ca_certs=ca_crt, certfile=client_crt, keyfile=client_key)
client.tls_insecure_set(True)

client.connect(broker_hostname, port)
client.loop_start()

topic = "idc/iris"
msg_count = 0

msg = []
msg.append(
    '[{"model":"iris-KNN"},{"SepalLengthCm":5.9,"SepalWidthCm":3,"PetalLengthCm":5.1,"PetalWidthCm":1}]'
)
msg.append(
    '[{"model":"iris-GNB"},{"SepalLengthCm":5.9,"SepalWidthCm":3,"PetalLengthCm":5.1,"PetalWidthCm":1}]'
)
msg.append(
    '[{"model":"iris-SVC"},{"SepalLengthCm":5.9,"SepalWidthCm":3,"PetalLengthCm":5.1,"PetalWidthCm":1}]'
)
msg.append(
    '[{"model":"iris-DT"},{"SepalLengthCm":5.9,"SepalWidthCm":3,"PetalLengthCm":5.1,"PetalWidthCm":1}]'
)
msg.append(
    '[{"model":"iris-LR"},{"SepalLengthCm":5.9,"SepalWidthCm":3,"PetalLengthCm":5.1,"PetalWidthCm":1}]'
)
msg.append(
    '[{"model":"iris-LDA"},{"SepalLengthCm":5.9,"SepalWidthCm":3,"PetalLengthCm":5.1,"PetalWidthCm":1}]'
)

try:
    while msg_count < len(msg):
        time.sleep(1)
        result = client.publish(topic, msg[msg_count])
        status = result[0]
        if status == 0:
            print("Message " + str(msg[msg_count]) + " is published to topic " + topic)
        else:
            print("Failed to send message to topic " + topic)
        msg_count += 1
finally:
    client.loop_stop()
