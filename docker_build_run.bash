#!/bin/bash

docker build -t medicwhizz_web:v1 .

docker run --publish 8000:8000 medicwhizz_web:v1

# docker ps -a
# docker rm <container id> [<container id>,]

# docker images
# docker rmi <image id> [<image id>,]
