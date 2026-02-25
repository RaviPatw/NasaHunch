#!/usr/bin/env python3
import os
import socket
import time

from prometheus_client import Gauge, start_http_server


THERMAL_PATH = "/host_sys/class/thermal/thermal_zone0/temp"
POLL_SECONDS = 5

temp_c = Gauge("pi_cpu_temperature_c", "Raspberry Pi CPU temperature in Celsius")
temp_available = Gauge(
    "pi_cpu_temperature_available", "1 if Pi CPU temperature file is available, else 0"
)
host_info = Gauge("pi_temp_exporter_info", "Static info for Pi temp exporter", ["hostname"])


def read_temp_c() -> float | None:
    try:
        with open(THERMAL_PATH, "r", encoding="utf-8") as f:
            raw = f.read().strip()
        # Raspberry Pi reports millidegrees C, e.g. 48123
        return float(raw) / 1000.0
    except Exception:
        return None


def main() -> None:
    start_http_server(9300)
    host_info.labels(hostname=socket.gethostname()).set(1)
    while True:
        temp = read_temp_c()
        if temp is None:
            temp_available.set(0)
        else:
            temp_available.set(1)
            temp_c.set(temp)
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
