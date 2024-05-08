#!/bin/bash

# Define variables
AMI_ID="ami-postgre"
KEY_PAIR_NAME="postgre-ec2-key"
VPC_CIDR_BLOCK="10.0.0.0/16"
SUBNET_CIDR_BLOCK="10.0.0.0/24"
POLICY_DOCUMENT_PATH="./PostgreSQL-IAM-policy.json"
IAM_ROLE_NAME="postgre-ec2-role"
IAM_INSTANCE_PROFILE_NAME="postgre-ec2-instance-profile"
SECURITY_GROUP_NAME="postgre-security-group"
EC2_INSTANCE_TYPE="t2.micro"
REGION="us-east-1"
SUBNET_AVAILABILITY_ZONE="us-east-1a"
SCRIPT_PATH="./setup.sh"

# Cleanup
docker compose down --volumes
docker compose up --detach
sudo rm "$KEY_PAIR_NAME"

# Create key pair
aws ec2 create-key-pair --key-name "$KEY_PAIR_NAME" --query 'KeyMaterial' --output text > "$KEY_PAIR_NAME.pem"
chmod 400 "$KEY_PAIR_NAME.pem"
echo "Created $KEY_PAIR_NAME"

# Create VPC
VPC_ID=$(aws ec2 create-vpc --cidr-block "$VPC_CIDR_BLOCK" --query 'Vpc.VpcId' --output text)
echo "Created $VPC_ID"

# Create subnet
SUBNET_ID=$(aws ec2 create-subnet --vpc-id "$VPC_ID" --cidr-block "$SUBNET_CIDR_BLOCK" --availability-zone "$SUBNET_AVAILABILITY_ZONE" --query 'Subnet.SubnetId' --output text)
echo "Created $SUBNET_ID"

# Create IAM role
IAM_ROLE_ARN=$(aws iam create-role --role-name "$IAM_ROLE_NAME" --assume-role-policy-document file://$POLICY_DOCUMENT_PATH  --output text --query 'Role.Arn')
echo "Created $IAM_ROLE_ARN"

# Attach IAM policy to the role (replace with your desired policy ARN)
aws iam attach-role-policy --role-name "$IAM_ROLE_NAME" --policy-arn "arn:aws:iam::aws:policy/AmazonEC2FullAccess"

# Create IAM instance profile
aws iam create-instance-profile --instance-profile-name "$IAM_INSTANCE_PROFILE_NAME"

# Add role to instance profile
aws iam add-role-to-instance-profile --instance-profile-name "$IAM_INSTANCE_PROFILE_NAME" --role-name "$IAM_ROLE_NAME"
echo "Created $IAM_INSTANCE_PROFILE_NAME"

# Create security group
SG_ID=$(aws ec2 create-security-group --group-name "$SECURITY_GROUP_NAME" --description "Security group for EC2 instance" --vpc-id "$VPC_ID" --query 'GroupId' --output text)
echo "Created $SG_ID"

# Add inbound rules to security group
aws ec2 authorize-security-group-ingress --group-id "$SG_ID" --protocol tcp --port 22 --cidr 0.0.0.0/0 --output text
aws ec2 authorize-security-group-ingress --group-id "$SG_ID" --protocol tcp --port 5432 --cidr 0.0.0.0/0 --output text
echo "Authorized $SG_ID to ports 22 and 5432"

AMI_ID="ami-ekslinux"
# Launch EC2 instance
INSTANCE_ID=$(aws ec2 run-instances --image-id "$AMI_ID" --instance-type "$EC2_INSTANCE_TYPE" --key-name "$KEY_PAIR_NAME" --subnet-id "$SUBNET_ID" --security-group-ids "$SG_ID" --associate-public-ip-address --iam-instance-profile Name="$IAM_INSTANCE_PROFILE_NAME" --region "$REGION" --user-data "$SCRIPT_PATH" --query 'Instances[0].InstanceId' --output text)
echo "Created EC2 instance $INSTANCE_ID"
