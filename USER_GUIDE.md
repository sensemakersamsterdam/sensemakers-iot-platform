# User Guide

## Access to the platform

All data in the platform is publicly available in the dashboards at https://grafana.sensemakersams.org/ without login.

Access to the platform is organised on a project basis. There is a dedicated account for every project within the Sensemakers community. Using this account, people can read/write data from/to the platform services. In addition, a public account exists that can be used to access all data within the platform.

The examples given below run from a command line and require the project password and the public password to be set an environment variables.

```bash
# Password for the account belonging to a test project
export TEST_PASSWORD=
# Password for the public account
export PUBLIC_PASSWORD=
```

## Data format for the incoming messages

Only the messages sent in the correct JSON format will be processed in the platform. The required format is:
- `app_id` (required) is the name/id of your project/application
- `dev_id` (required) is the name/id of the device sending data
- `payload_fields` (required) is the dictionary of values, e.g. `{"temperature": 42, "humidity": 42}`
- `time` (optional) is the time of the measurement in milliseconds. If not specified, the time of arrival to the platform will be used.
- `tag_fields` (optional) is the dictionary of any other key-value pairs you might want to use to classify the time series, e.g. `{"location": "Amsterdam"}`. These tags will be used by InfluxDB.

## Send messages over MQTT

Clients can send messages to topics `pipeline/app_id/dev_id` where `app_id` has to correspond to the username used for sending data to the MQTT broker.

The following table shows the access rights for different users:

| | **admin** user | **app_id_1** user | **app_id_2** user | **public** user |
| :---- | :---- | :---- | :---- | :---- |
| any topic | read/write | n/a | n/a | read-only |
| **pipeline/app_id_1** topic | read/write | read/write | n/a | read-only |
| **pipeline/app_id_2** topic | read/write | n/a | read/write | read-only |

Send messages using the predefined user/project `test`:

```bash
# Send a single message.
mosquitto_pub -t pipeline/test/test -h mqtt.sensemakersams.org -p 31090 -u test -P $TEST_PASSWORD -m '{"app_id": "test", "dev_id": "test", "payload_fields": {"temperature": 42, "humidity": 42}}'

# Send a number of random messages.
for i in {1..100}
do
  mosquitto_pub -t pipeline/test/test -h mqtt.sensemakersams.org -p 31090 -u test -P $TEST_PASSWORD -m '{"app_id": "test", "dev_id": "test", "payload_fields": {"temperature": '$((RANDOM%10))'}}'
done
```

Advanced usage:

```bash
# Send a message with additional tags that will be used by InfluxDB.
mosquitto_pub -t pipeline/test/test -h mqtt.sensemakersams.org -p 31090 -u test -P $TEST_PASSWORD -m \
  '{"app_id": "test", "dev_id": "test", "payload_fields": {"temperature": 42}, "tag_fields": {"location": "Amsterdam"}}'

# A timestamp is assigned to every message once it arrives to the platform over MQTT.
# This timestamp can be overwriten with a custom timestamp in milliseconds specified within the message.
mosquitto_pub -t pipeline/test/test -h mqtt.sensemakersams.org -p 31090 -u test -P $TEST_PASSWORD -m \
  '{"app_id": "test", "dev_id": "test", "payload_fields": {"temperature": 42}, "time": 1601209319000}'
```

Listen for the incoming messages in real-time.

```bash
# Listen to all messages.
mosquitto_sub -t pipeline/# -h mqtt.sensemakersams.org -p 31090 -u public -P $PUBLIC_PASSWORD

# Listen to all messages from a single application.
mosquitto_sub -t pipeline/test/+ -h mqtt.sensemakersams.org -p 31090 -u public -P $PUBLIC_PASSWORD

# Listen to all messages from a single device.
mosquitto_sub -t pipeline/test/test -h mqtt.sensemakersams.org -p 31090 -u public -P $PUBLIC_PASSWORD
```

MQTT version 5 supports shared subscriptions where the messages from a topic are load-balanced among several clients.

```bash
# Listen to topic pipeline as client1 within group1.
mosquitto_sub -t '$share/group1/pipeline' -i client1 -h mqtt.sensemakersams.org -p 31090 -u public -P $PUBLIC_PASSWORD

# Listen to topic pipeline as client2 within group1.
mosquitto_sub -t '$share/group1/pipeline' -i client2 -h mqtt.sensemakersams.org -p 31090 -u public -P $PUBLIC_PASSWORD
```

## Send messages over HTTPS

```bash
curl -XPOST https://openfaas.sensemakersams.org/function/faas-mqtt --data '{"app_id": "test", "dev_id": "test", "payload_fields": {"temperature": 42}}' -H "X-Api-Key:$TEST_PASSWORD"
```

The entry point works well with [The Things Network HTTP integration](https://www.thethingsnetwork.org/docs/applications/http/).
In principle, `app_id` used in The Things Network does not have to coincide with `app_id` used in this platform. It is possible to override `app_id` in a URL query paramter, e.g. `https://openfaas.sensemakersams.org/function/faas-mqtt?app_id=test_project`.

A URL query paramter can also be used to override the MQTT user, which is identical from `app_id` otherwise. This is useful when sending data for multiple projects as the admin user.

```bash
curl –XPOST https://openfaas.sensemakersams.org/function/faas-mqtt?mqtt_user=admin --data \
  '{"app_id": "test", "dev_id": "test", "payload_fields": {"temperature": 42}}’ \
  -H "X-Api-Key:$ADMIN_PASSWORD"
```

## InfluxDB

Show raw messages:

```bash
influx -host influxdb.sensemakersams.org -port 443 -ssl -username public -password $PUBLIC_PASSWORD -database raw -execute "SHOW MEASUREMENTS"
influx -host influxdb.sensemakersams.org -port 443 -ssl -username public -password $PUBLIC_PASSWORD -database raw -execute "SHOW SERIES"

influx -host influxdb.sensemakersams.org -port 443 -ssl -username public -password $PUBLIC_PASSWORD -database raw -precision rfc3339 -execute "SELECT * FROM /.*/"

# Show the last message.
influx -host influxdb.sensemakersams.org -port 443 -ssl -username public -password $PUBLIC_PASSWORD -database raw -precision rfc3339 -execute "SELECT * FROM /.*/ ORDER BY DESC LIMIT 1"
```

Show processed messages:

```bash
influx -host influxdb.sensemakersams.org -port 443 -ssl -username public -password $PUBLIC_PASSWORD -database iot -execute "SHOW MEASUREMENTS"
influx -host influxdb.sensemakersams.org -port 443 -ssl -username public -password $PUBLIC_PASSWORD -database iot -execute "SHOW SERIES"

influx -host influxdb.sensemakersams.org -port 443 -ssl -username public -password $PUBLIC_PASSWORD -database iot -precision rfc3339 -execute "SELECT * FROM /.*/"

# Show the last message.
influx -host influxdb.sensemakersams.org -port 443 -ssl -username public -password $PUBLIC_PASSWORD -database iot -precision rfc3339 -execute "SELECT * FROM /.*/ ORDER BY DESC LIMIT 1"
```

Tags for `app_id` and `dev_id` are available for both raw and processed messages.

Select the messages belonging to a specific application or device:

```bash
# Select the messages belonging to a specific application or device.
influx -host influxdb.sensemakersams.org -port 443 -ssl -username public -password $PUBLIC_PASSWORD -database iot -precision rfc3339 -execute "SELECT * FROM \"test/test\""

# Select the messages belonging to a specific application.
influx -host influxdb.sensemakersams.org -port 443 -ssl -username public -password $PUBLIC_PASSWORD -database iot -precision rfc3339 -execute "SELECT * FROM /test\/.*/"
influx -host influxdb.sensemakersams.org -port 443 -ssl -username public -password $PUBLIC_PASSWORD -database iot -precision rfc3339 -execute "SELECT * FROM /.*/ WHERE app_id='test'"

# Select the messages belonging to a specific device accross all applications.
influx -host influxdb.sensemakersams.org -port 443 -ssl -username public -password $PUBLIC_PASSWORD -database iot -precision rfc3339 -execute "SELECT * FROM /.*\/test/"
influx -host influxdb.sensemakersams.org -port 443 -ssl -username public -password $PUBLIC_PASSWORD -database iot -precision rfc3339 -execute "SELECT * FROM /.*/ WHERE dev_id='test'"
```

Download messages in a csv format:

```bash
influx -host influxdb.sensemakersams.org -port 443 -ssl -username public -password $PUBLIC_PASSWORD -database iot -precision rfc3339 -format csv -execute "SELECT * FROM /.*/ WHERE app_id='test'"
```

## Grafana

All messages from the InfluxDB database can be viewed in the Grafana dashboards available at https://grafana.sensemakersams.org
