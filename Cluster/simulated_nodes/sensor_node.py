from prometheus_client import start_http_server, Gauge
import requests, random, socket, time

# -------------------------------
# Django API endpoint
# -------------------------------
URL_REGISTER = "http://backend:8000/register"
URL_METRICS = "http://backend:8000/report_metrics"

# Unique hostname for the node
HOSTNAME = f"sensor_node_{random.randint(1, 100)}"
IP = "127.0.0.1"  # can replace with real Pi IP later

# -------------------------------
# Register node with Django
# -------------------------------
try:
    requests.post(URL_REGISTER, json={"hostname": HOSTNAME, "ip": IP})
    print(f"Registered node {HOSTNAME} with Django")
except Exception as e:
    print(f"Failed to register node: {e}")

# -------------------------------
# Prometheus metrics
# -------------------------------
cpu_g = Gauge("cpu_usage_pct", "CPU Usage %")
mem_g = Gauge("memory_usage_pct", "Memory Usage %")
disk_g = Gauge("disk_usage_pct", "Disk Usage %")
temp_g = Gauge("sensor_temperature_c", "Temperature in Celsius")
hum_g = Gauge("sensor_humidity_pct", "Humidity in %")

# Start Prometheus HTTP server
start_http_server(9200)  # Prometheus scrapes this port

# -------------------------------
# Main loop: generate metrics
# -------------------------------
while True:
    # Simulated metrics
    cpu = random.randint(5, 80)
    memory = random.randint(20, 90)
    disk = random.randint(10, 70)
    temp = random.uniform(20, 40)
    hum = random.uniform(40, 80)

    # Update Prometheus metrics
    cpu_g.set(cpu)
    mem_g.set(memory)
    disk_g.set(disk)
    temp_g.set(temp)
    hum_g.set(hum)

    # Send metrics to Django for permanent storage
    try:
        requests.post(URL_METRICS, json={
            "hostname": HOSTNAME,
            "cpu": cpu,
            "memory": memory,
            "disk": disk,
            "temperature": temp,
            "humidity": hum
        })
    except Exception as e:
        print(f"Failed to send metrics to Django: {e}")

    # Optional: console output for debugging
    print(f"Metrics sent: CPU={cpu}, MEM={memory}, DISK={disk}, TEMP={temp:.1f}°C, HUM={hum:.1f}%")

    time.sleep(5)
