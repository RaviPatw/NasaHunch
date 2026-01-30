# Application Deployment Contract

This document defines the requirements for applications passed into the NASA HUNCH Application Server Farm.

## Accepted Application Formats
An application must provide ONE of the following:
1. A public Docker image
2. A Git repository containing a Dockerfile

## Required
- Containerized application
- Exposed service port
- Runs without manual configuration

## Optional
- Environment variables
- Resource limits (CPU, memory)
- Node placement constraints (AI or CPU nodes)

## Deployment Method
Applications are deployed using Docker Swarm orchestration and are monitored using Prometheus and Grafana.

If an application meets this contract, it can be deployed and hosted by the system without modification.
