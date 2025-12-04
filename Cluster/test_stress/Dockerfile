FROM ubuntu:24.04
RUN apt-get update && apt-get install -y stress-ng
CMD ["stress-ng", "--cpu", "2", "--timeout", "60s"]
