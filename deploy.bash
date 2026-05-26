#!/bin/bash

echo "github user: $GH_USER..."

echo "Path is $PATH" >> tmp.log

echo "*** Attempting Docker Login..."
echo $GH_PAT | docker login ghcr.io -u $GH_USER --password-stdin

echo "*** Attempting Docker Pull..."
docker pull $GH_URL

echo "*** Attempting Docker Stop and Rm on ${GH_NAME}..."
OUTPUT=$(docker stop $GH_NAME 2>&1)
if [ "$OUTPUT" = $GH_NAME ]; then
    OUTPUT=$(docker rm $GH_NAME 2>&1)
else
    echo "No container to stop"
fi
if [ "$OUTPUT" = $GH_NAME ]; then
    echo "Existing ${GH_NAME} container stopped"
fi

 echo "*** Attemping Docker Run..."
CONTAINER_ID=$(docker run -d \
--name $GH_NAME \
--restart unless-stopped \
--volume "${CONFIG_LOCATION}:/app/application.yaml:ro" \
$GH_URL)

if [ -n "$CONTAINER_ID" ]; then
    echo "*** docker run successful! Container ID: ${CONTAINER_ID:0:12}"
else
    echo "docker run failed"
    exit 1
fi

sleep 2 
docker ps --filter "id=${CONTAINER_ID}"
