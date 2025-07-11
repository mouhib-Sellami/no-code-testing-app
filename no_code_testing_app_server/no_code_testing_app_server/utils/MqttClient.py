from no_code_testing_app_server.patterns.Singleton import singleton
import paho.mqtt.client as mqtt
import threading
import atexit
import os
import logging
import json
from typing import Callable, Optional
from termcolor import colored

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - 🌟 %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "doker.host.internat")
BROKER_PORT = int(os.getenv("EMQX_MQTT_TCP_PORT", 1883))
USER_NAME = os.getenv("EMQX_DEFAULT_USERNAME", "default")
PASSWORD =os.getenv("EMQX_DEFAULT_PASSWORD", "default")
DEFAULT_QOS = 1


@singleton
class MQTTClient:
    def __init__(self):
        self.client = mqtt.Client(client_id="default_app")
        self.client.username_pw_set(
            username=USER_NAME,
            password=PASSWORD
        )
        self._is_running = False
        self._lock = threading.Lock()
        self.topics = {}
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        self.client.on_subscribe = self.on_subscribe
        self.thread: Optional[threading.Thread] = None
        atexit.register(self._cleanup)
        self.connect()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info(colored(
                f"🚀 Connected to the server !", "cyan"))
            self._is_running = True
            self.init_handlers()

        else:
            logger.error(
                colored(f"💥 Connection crashed with code {rc}! Retry later!", "red"))
            raise ConnectionError(f"Connection failed with code {rc}")

    def on_disconnect(self, client, userdata, rc):
        self._is_running = False
        if rc != 0:
            logger.warning(
                colored(f"😱 Unexpected disconnect! Reason code: {rc}", "yellow"))
        else:
            logger.info(
                colored("👋 Gracefully disconnected from the MQTT universe!", "blue"))

    def _run(self):
        try:
            self.client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
            logger.info(
                colored("🌌 Agent client connected and ready to rock!", "cyan"))
            self.client.loop_start()
        except Exception as e:
            self._is_running = False
            logger.error(colored(f"💥 Failed to connect to MQTT: {e}", "red"))
            raise

    def connect(self):
        if not self._is_running and (self.thread is None or not self.thread.is_alive()):
            self.thread = threading.Thread(target=self._run)
            self.thread.daemon = True
            self.thread.start()

    def _cleanup(self):
        logger.info(colored("🧹 Cleaning up agent", "blue"))
        self._is_running = False
        self.client.loop_stop()
        self.client.disconnect()
        if self.thread is not None and self.thread.is_alive():
            self.thread.join(timeout=2.0)
            self.thread = None

    def disconnect(self):
        logger.info(colored("🎉 Wrapping up the agent party!", "blue"))
        self._cleanup()

    def init_handlers(self):
        pass
        # logging.info("subscribing")
        # self.subscribe(f"{str(self.agent_config.agent_key)}_health_check", DEFAULT_QOS, self.handler.handle_health_check)
        # self.subscribe(f"{str(self.agent_config.agent_key)}_new_project", DEFAULT_QOS, self.handler.handle_new_project)
        # logging.info("subscribing")

    def on_message(self, client, userdata, msg):
        with self._lock:
            logging.info(self.topics)
            callback = self.topics.get(msg.topic)
            if callback != None:
                logging.info("not none")
                logging.info(callback)
                callback(msg.payload.decode())

    def subscribe(self, topic, qos=0, cb=None):
        with self._lock:
            try:
                if not self._is_running:
                    self.connect()
                result, mid = self.client.subscribe(topic, qos=qos)
                logging.info(result)
                if result == mqtt.MQTT_ERR_SUCCESS:
                    logging.info("here")
                    self.topics.update({topic: cb})
                logging.info(self.topics)
            except Exception as e:
                logging.info(f"Subscription error: {e}")

    def on_subscribe(self, client, userdata, mid, granted_qos):
        logging.info(f"Subscribed to topic with QoS: {granted_qos}")

    def publish(self, topic, msg, qos=1):
         with self._lock:
            try:
                if not self._is_running:
                    self.connect()
                self.client.publish(topic, msg, qos)
            except Exception as e:
                logging.info(f"Subscription error: {e}")