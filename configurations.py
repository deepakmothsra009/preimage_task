import os

PROJECT_FOLDER = "/Users/dkm/data/project_data"
S3_DATA_PATH = "/Users/dkm/data/s3_data"
EXTERNAL_RABBITMQ_HOST = "localhost"

if os.environ.get("PROJECT_ENV") == "docker":
    from docker_configurations import *
