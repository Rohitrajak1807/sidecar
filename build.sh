#!/bin/bash

DOCKER_BUILDKIT=1 docker build --secret id=user_name,src=.user --secret id=pass,src=.pass -f Dockerfile