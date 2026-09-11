#!/bin/sh
set -eu

DOCKER_DESKTOP_BIN="/Applications/Docker.app/Contents/Resources/bin"
if [ -x "$DOCKER_DESKTOP_BIN/docker-credential-desktop" ]; then
  PATH="$DOCKER_DESKTOP_BIN:$PATH"
  export PATH
fi
if [ -z "${DOCKER_HOST:-}" ] && [ -S "$HOME/.docker/run/docker.sock" ]; then
  DOCKER_HOST="unix://$HOME/.docker/run/docker.sock"
  export DOCKER_HOST
fi

SERVICE_NAME="${SERVICE_NAME:-dividend-tracker-demo}"
REGION="${AWS_REGION:-$(aws configure get region)}"
REGION="${REGION:-us-east-1}"
IMAGE_NAME="${SERVICE_NAME}:latest"

if ! command -v lightsailctl >/dev/null 2>&1; then
  echo "lightsailctl is required to upload images. Install it with: brew install aws/tap/lightsailctl" >&2
  exit 1
fi

docker build --platform linux/amd64 --tag "$IMAGE_NAME" .

if ! aws lightsail get-container-services --service-name "$SERVICE_NAME" --region "$REGION" >/dev/null 2>&1; then
  aws lightsail create-container-service \
    --service-name "$SERVICE_NAME" \
    --power nano \
    --scale 1 \
    --region "$REGION"
fi

IMAGE_UPLOAD_OUTPUT="$(aws lightsail push-container-image \
  --service-name "$SERVICE_NAME" \
  --label web \
  --image "$IMAGE_NAME" \
  --region "$REGION")"
IMAGE_REFERENCE="$(printf '%s\n' "$IMAGE_UPLOAD_OUTPUT" | sed -n 's/.*Refer to this image as "\(.*\)" in deployments.*/\1/p')"

if [ -z "$IMAGE_REFERENCE" ]; then
  echo "Lightsail did not return an image reference:" >&2
  printf '%s\n' "$IMAGE_UPLOAD_OUTPUT" >&2
  exit 1
fi

aws lightsail create-container-service-deployment \
  --service-name "$SERVICE_NAME" \
  --containers "{\"web\":{\"image\":\"$IMAGE_REFERENCE\",\"ports\":{\"8080\":\"HTTP\"}}}" \
  --public-endpoint "containerName=web,containerPort=8080,healthCheck={path=/health}" \
  --region "$REGION"

aws lightsail get-container-services \
  --service-name "$SERVICE_NAME" \
  --region "$REGION" \
  --query 'containerServices[0].url' \
  --output text