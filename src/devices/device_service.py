import logging

from paho.mqtt.client import Client as MQTTClient

logger = logging.Logger(__name__)

class DeviceService:
    def __init__(self, mqtt_client: MQTTClient):
        self._mqtt_client = mqtt_client
        self._mqtt_client.on_connect = self.on_connect

    def on_connect(self, client, userdata, flags, rc):
        logger.info(f"Connected with result code: {str(rc)}, {userdata}, {flags}")

    def on_message(self, client, userdata, msg):
        logger.info(f"Received {userdata}, {str(msg.payload)}")
