# async-httpd-data-collector

Interface handling the communication between sensory data-emitting devices, InfluxDB and the user.

Module interface.py asyncronously manages fetching data from device and storing it in the databasa in the background,
while allowing for querying the database at the same time.

