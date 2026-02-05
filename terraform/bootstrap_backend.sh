#!/bin/bash
set -e

REGION="ap-southeast-2"
PROJECT_NAME="self-healing-devsecops"
BUCKET_NAME="${PROJECT_NAME}-tfstate-$(date +%s)"
TABLE_NAME="${PROJECT_NAME}-tf-lock"

echo "Creating S3 Bucket: $BUCKET_NAME..."
if aws s3api head-bucket --bucket "$BUCKET_NAME" 2>/dev/null; then
  echo "Bucket already exists."
else
  aws s3api create-bucket --bucket "$BUCKET_NAME" --region "$REGION" --create-bucket-configuration LocationConstraint="$REGION"
  aws s3api put-bucket-versioning --bucket "$BUCKET_NAME" --versioning-configuration Status=Enabled
  echo "Bucket created."
fi

echo "Creating DynamoDB Table: $TABLE_NAME..."
if aws dynamodb describe-table --table-name "$TABLE_NAME" --region "$REGION" >/dev/null 2>&1; then
  echo "Table already exists."
else
  aws dynamodb create-table \
    --table-name "$TABLE_NAME" \
    --attribute-definitions AttributeName=LockID,AttributeType=S \
    --key-schema AttributeName=LockID,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region "$REGION"
  echo "Table created."
fi

# Update backend.tf with the actual bucket name (replacing placeholder)
if [[ "$OSTYPE" == "darwin"* ]]; then
  sed -i '' "s/self-healing-devsecops-tfstate-placeholder/$BUCKET_NAME/g" terraform/environments/dev/backend.tf
else
  sed -i "s/self-healing-devsecops-tfstate-placeholder/$BUCKET_NAME/g" terraform/environments/dev/backend.tf
fi

echo "Backend bootstrap complete. Updated backend.tf with bucket: $BUCKET_NAME"
