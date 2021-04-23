# -*- coding: utf-8 -*-
"""Query data in InfluxDB."""

from influxdb import InfluxDBClient
import os

influxdb_host = "influxdb.sensemakersams.org"
influxdb_port = 443
influxdb_user = "public"
influxdb_password = os.environ["PUBLIC_PASSWORD"]
influxdb_dbname = "iot"

client = InfluxDBClient(
    influxdb_host,
    influxdb_port,
    influxdb_user,
    influxdb_password,
    influxdb_dbname,
    ssl=True,
    verify_ssl=True,
)

rs = client.query("SELECT * FROM /.*/ WHERE app_id='test'", epoch="ms")

# Get raw JSON response.
raw = rs.raw

# Get points.
# The measurement in InfluxDB can be specified. The format of the measurements is app_id/dev_id.
# points = rs.get_points(measurement='test/test', tags={'dev_id': 'test'})
points = rs.get_points()

for point in points:
    print(f"Time: {point['time']}, Temperature: {point['temperature']}")
