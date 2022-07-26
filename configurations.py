import os

PROJECT_FOLDER = "/home/deepak/data/project_data"
S3_DATA_PATH = "/home/deepak/data/s3_data"
RABBITMQ_HOST = "localhost"
POSTGRES_HOST = "localhost"
SAMPLE_PROJECT_PATH = "/home/deepak/preimage_task/projects/"

if os.environ.get("PROJECT_ENV") == "docker":
    from docker_configurations import *
