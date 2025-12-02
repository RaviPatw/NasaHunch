import requests, random, socket, time

URL_REGISTER = "http://backend:8000/register"
URL_METRICS = "http://backend:8000/report_metrics"

HOSTNAME = f"sim-node-{random.randint(1,100)}"
IP = "127.0.0.1"

# Register node
requests.post(URL_REGISTER, json={"hostname": HOSTNAME, "ip": IP})

while True:
    cpu = random.randint(5, 80)
    memory = random.randint(20, 90)
    disk = random.randint(10, 70)
    requests.post(URL_METRICS, json={"hostname": HOSTNAME, "cpu": cpu, "memory": memory, "disk": disk})
    print(f"Sent metrics: CPU={cpu}, Memory={memory}, Disk={disk}")
    time.sleep(5)