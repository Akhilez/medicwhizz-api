#!/bin/bash
set -x

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $DIR

PROJECT_ID="medicwhizz_web"
IMAGE_NAME="medicwhizz_web"
CLOUD_RUN_SERVICE="medicwhizz_web"

gcloud builds submit --tag gcr.io/$PROJECT_ID/$IMAGE_NAME:v1 $DIR

gcloud beta run deploy $CLOUD_RUN_SERVICE --image=gcr.io/$PROJECT_ID/$IMAGE_NAME:v1 --allow-unauthenticated --memory=512Mi --timeout=900 --platform managed --set-env-vars=DJANGO_DEBUG=False
