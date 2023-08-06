import boto3
from .config import config

# Get the service resource.
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

# Retrieve the table to store the Thread ID and Student ID
# for the purpose of tracking answers and creating an archive for each student's questions.
student_thread = dynamodb.Table(config['students_db_table'])