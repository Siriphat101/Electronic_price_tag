from flask import Flask
from paho.mqtt.client import Client

client = Client()


app = Flask(__name__)

# MQTT client
client = Client()

@app.route('/')
def index():
    # Enable TLS for secure connection
    client.tls_set(tls_version=client.ssl.PROTOCOL_TLS)
    # Set username and password
    client.username_pw_set("flaskweb", "123456789")
    # Connect to HiveMQ Cloud on port 8883 (default for MQTT)
    client.connect("d706dce9e3774e1290f4d4d0458c77aa.s1.eu.hivemq.cloud", 8883)

    # Publish a message to the topic
    client.publish('my_topic', 'Hello, MQTT!')

    return 'Message published to MQTT topic!'

if __name__ == '__main__':
    app.run()
