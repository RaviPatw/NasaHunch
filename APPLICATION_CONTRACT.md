# Application Deployment Contract

This document defines the requirements for applications passed into the NASA HUNCH Application Server Farm.

## Accepted Application Formats
An application contract must provide exactly ONE source:
1. `image`: public/private Docker image reference
2. `git_repo`: Git repository URL containing a Dockerfile

## Required Fields
- `name`: Docker Swarm service name (lowercase, 2-63 chars)
- `type`: `ai`, `general`, or `web` (used for node placement)
- `replicas`: number of service replicas (>=1)
- Source:
  - image source: `image`
  - git source: `git_repo`

## Optional Fields
- `port`: application port inside container
- `publish_port`: host port to publish (if omitted, random port is used)
- `env`: key/value environment variables
- `cpu_limit`: swarm CPU limit, example `1.5`
- `memory_limit`: swarm memory limit, example `2g`
- `constraints`: additional swarm constraints
- `network`: swarm overlay network name
- Git source extras:
  - `git_ref`: branch/tag/commit
  - `dockerfile`: Dockerfile path inside build context (default `Dockerfile`)
  - `build_context`: Docker build context path (default `.`)
- Runtime command override:
  - `command`: command to run
  - `args`: array of command arguments

## Deployment Method
Applications are deployed by `deployer/deployer.py` using Docker Swarm and are monitored with Prometheus/Grafana.

If an application meets this contract, it can be deployed and hosted by the system without modification.
