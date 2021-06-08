#!/bin/bash

docker rm -f flag_leak
docker build -t flag_leak . && \
docker run --name=flag_leak --rm -p1337:80 -it flag_leak