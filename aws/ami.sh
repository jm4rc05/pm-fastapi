#!/bin/bash

# Define variables
IMAGE_NAME="postgre"
DOCKERFILE_PATH="./PostgreSQL.dockerfile"

BUCKET_PREFIX="temporary-bucket"
UNIQUE_SUFFIX=$(openssl rand -hex 16)
BUCKET_NAME="$BUCKET_PREFIX-$UNIQUE_SUFFIX"

REGION="us-east-1"
IMAGE_DEF_PATH="file://PostgreSQL-image.json"

# Create container
podman build --tag $IMAGE_NAME --file $DOCKERFILE_PATH

# Export image
podman save $IMAGE_NAME > $IMAGE_NAME.tar
echo "Created $IMAGE_NAME.tar"

# Create the S3 bucket
aws s3api create-bucket --bucket "$BUCKET_NAME" --region $REGION
echo "Created $BUCKET_NAME"

# Upload tar image to S3 bucket
aws s3 cp $IMAGE_NAME.tar s3://$BUCKET_NAME/$IMAGE_NAME.tar
echo "Uploaded $IMAGE_NAME to $BUCKET_NAME"

# Import image to EC2
IMAGE_ID=$(aws ec2 import-image --cli-input-json $IMAGE_DEF_PATH --query 'ImageId' --output json)

echo "Created AMI $IMAGE_ID for $IMAGE_NAME"
