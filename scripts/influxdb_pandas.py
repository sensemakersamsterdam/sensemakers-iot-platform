# -*- coding: utf-8 -*-
"""Read data from InfluxDB into Pandas DataFrame."""

from influxdb import DataFrameClient
import os

influxdb_host = "influxdb.sensemakersams.org"
influxdb_port = 443
influxdb_user = "public"
influxdb_password = os.environ["PUBLIC_PASSWORD"]
influxdb_dbname = "iot"

client = DataFrameClient(
    influxdb_host,
    influxdb_port,
    influxdb_user,
    influxdb_password,
    influxdb_dbname,
    ssl=True,
    verify_ssl=True,
)

# Query returns a dictionary of dataframes.
rs = client.query(
    "SELECT * FROM /.*/ WHERE app_id='test'", chunked=True, chunk_size=10000
)
print(rs.keys())

# The measurement in InfluxDB can be specified. The format of the measurements is app_id/dev_id.
df = rs["test/test"]
print(df.head())
