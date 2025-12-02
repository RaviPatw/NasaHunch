from prometheus_client import start_http_server, Gauge
import random, time

temp_g = Gauge("sensor_temperature_c", "Temperature")
hum_g = Gauge("sensor_humidity_pct", "Humidity")

start_http_server(9200)

while True:
    temp_g.set(random.uniform(20, 40))
    hum_g.set(random.uniform(40, 80))
    time.sleep(5)
