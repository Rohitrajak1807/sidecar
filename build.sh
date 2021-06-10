#!/bin/bash
DOCKER_GATEWAY_HOST=172.17.0.1
DOCKER_BUILDKIT=1 docker build --add-host=host.docker.internal:${DOCKER_GATEWAY_HOST} --secret id=user_name,src=./.user --secret id=pass,src=./.pass -f Dockerfile