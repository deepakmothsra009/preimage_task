import os

PROJECT_FOLDER = "/Users/dkm/data/project_data"
S3_DATA_PATH = "/Users/dkm/data/s3_data"
RABBITMQ_HOST = "localhost"
POSTGRES_HOST = "localhost"
SAMPLE_PROJECT_PATH = "/Users/dkm/preimage_task/projects/"

if os.environ.get("PROJECT_ENV") == "docker":
    from docker_configurations import *
