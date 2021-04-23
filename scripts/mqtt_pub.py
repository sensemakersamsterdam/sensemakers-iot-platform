# -*- coding: utf-8 -*-
"""Publish data to an MQTT topic."""

import paho.mqtt.publish as publish
import os
import json
import time

mqtt_host = "mqtt.sensemakersams.org"
mqtt_port = 31090
mqtt_user = "test"
mqtt_password = os.environ["TEST_PASSWORD"]

msg_json = {
    # The message will be processed by the platform and stored in a database only if app_id corresponds to the MQTT username.
    "app_id": "test",
    "dev_id": "test",
    "payload_fields": {"temperature": 42, "humidity": 42},
    # Epoch timestamp in milliseconds
    "time": int(time.time() * 1e3),
}
msg_str = json.dumps(msg_json)

auth = {"username": mqtt_user, "password": mqtt_password}
publish.single(
    "pipeline/test/test", payload=msg_str, hostname=mqtt_host, port=mqtt_port, auth=auth
)
