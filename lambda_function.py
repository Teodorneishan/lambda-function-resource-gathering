import os
import boto3
import mysql.connector

def list_vpcs_subnets():
    # AWS Credentials - Replace with your IAM user's Access Key ID and Secret Access Key
    #aws_access_key_id = os.environ['AWS_ACCESS_KEY_IDA']
    #aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEYA']

    # Replace these with your MariaDB database connection details
    db_host = os.environ['DB_HOST']
    db_port = os.environ['DB_PORT']
    db_name = os.environ['DB_NAME']
    db_user = os.environ['DB_USER']
    db_password = os.environ['DB_PASSWORD']

    # Validate required environment variables
    if not all([db_host, db_port, db_name, db_user, db_password]):
        raise ValueError("Missing required environment variables for database connection.")

    # Create AWS EC2 client
    ec2_client = boto3.client('ec2')

    try:
        # Retrieve VPCs
        vpcs_response = ec2_client.describe_vpcs()
        vpcs = vpcs_response['Vpcs']

        # Retrieve Subnets
        subnets_response = ec2_client.describe_subnets()
        subnets = subnets_response['Subnets']

        return vpcs, subnets

    except Exception as e:
        print(f"Error: {e}")
        return [], []

def save_to_database(vpcs, subnets):
    # Connect to the MariaDB database
    try:
        connection = mysql.connector.connect(
            host=os.environ['DB_HOST'],
            port=os.environ['DB_PORT'],
            database=os.environ['DB_NAME'],
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASSWORD']
        )

        cursor = connection.cursor()

        # Save VPCs to the database
        for vpc in vpcs:
            vpc_id = vpc['VpcId']
            vpc_cidr = vpc['CidrBlock']
            cursor.execute("INSERT INTO vpcs (vpc_id, cidr_block) VALUES (%s, %s)", (vpc_id, vpc_cidr))

        # Save Subnets to the database
        for subnet in subnets:
            subnet_id = subnet['SubnetId']
            subnet_cidr = subnet['CidrBlock']
            vpc_id = subnet['VpcId']
            cursor.execute("INSERT INTO subnets (subnet_id, cidr_block, vpc_id) VALUES (%s, %s, %s)", (subnet_id, subnet_cidr, vpc_id))

        connection.commit()
        cursor.close()
        connection.close()
        print("Data saved to the database successfully!")

    except Exception as e:
        print(f"Error: {e}")

def lambda_handler(event, context):
    vpcs, subnets = list_vpcs_subnets()
    save_to_database(vpcs, subnets)
    print("Available VPCs:")
    for vpc in vpcs:
        print(f"VPC ID: {vpc['VpcId']}, CIDR Block: {vpc['CidrBlock']}")
    
    print("\nAvailable Subnets:")
    for subnet in subnets:
        print(f"Subnet ID: {subnet['SubnetId']}, CIDR Block: {subnet['CidrBlock']}")
    return {
        'statusCode': 200,
        'body': 'Data saved to the database successfully!'
    }