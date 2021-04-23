# -*- coding: utf-8 -*-
"""Subscribe to an MQTT topic."""

import paho.mqtt.client as mqtt
import json
import os


def on_connect(mqttc, obj, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    # Listen to all messages.
    mqttc.subscribe("pipeline/#", qos=0)
    # Listen to all messages from a project.
    # mqttc.subscribe("pipeline/test/+", qos=0)
    # Listen to all messages from a device within a project.
    # mqttc.subscribe("pipeline/test/test", qos=0)


def on_disconnect(mqttc, obj, rc):
    if rc != 0:
        print("Unexpected disconnection.")


def on_message(mqttc, obj, msg):
    print(
        "Received message '"
        + str(msg.payload)
        + "' on topic '"
        + msg.topic
        + "' with QoS "
        + str(msg.qos)
    )

    msg_json = json.loads(str(msg.payload.decode("utf-8")))
    print(json.dumps(msg_json, indent=4, sort_keys=True))


def on_publish(mqttc, obj, mid):
    print("Messaged ID: " + str(mid))


def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_log(mqttc, obj, level, string):
    print(level, string)


mqttc = mqtt.Client()

mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe

mqtt_host = "mqtt.sensemakersams.org"
mqtt_port = 31090
# mqtt_user = "public"
# mqtt_password = os.environ["PUBLIC_PASSWORD"]
mqtt_user = "test"
mqtt_password = os.environ["TEST_PASSWORD"]

mqttc.username_pw_set(mqtt_user, mqtt_password)
mqttc.connect(mqtt_host, mqtt_port, 60)

mqttc.loop_forever()
