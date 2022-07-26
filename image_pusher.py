import pika
import sys
import os, shutil
import pickle
import multiprocessing as mp
from configurations import S3_DATA_PATH, SAMPLE_PROJECT_PATH


def send_data_to_injester(s3_project_path, project_meta_dict):
    """
    this function is used to send p3 project path to injestor
    """
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
    channel = connection.channel()
    channel.exchange_declare(exchange="injestor", exchange_type="fanout")
    message = pickle.dumps((s3_project_path, project_meta_dict))
    channel.basic_publish(exchange="injestor", routing_key="", body=message)
    print(" [x] Sent %r" % message)
    connection.close()


def copy_image(source_path, dest_path):
    shutil.copy(source_path, dest_path)


def upload_images_to_s3(project_name):
    """
    we are not actually storing the data in s3 here, but storing files locally
    """
    project_folder = os.path.join(SAMPLE_PROJECT_PATH, project_name)
    images_list = os.listdir(project_folder)
    dest_folder = os.path.join(S3_DATA_PATH, project_name)
    os.makedirs(dest_folder, exist_ok=True)
    for image in images_list:
        source_path = os.path.join(project_folder, image)
        dest_path = os.path.join(dest_folder, image)
        copy_image(source_path, dest_path)


"""
This script is used to send latest project data to the injestor
"""
if __name__ == "__main__":
    user_name = sys.argv[1] if len(sys.argv) > 1 else None
    project_name = sys.argv[2] if len(sys.argv) > 2 else None
    if not project_name:
        sys.stderr.write("Usage: %s [user_name] [project_name] \n" % sys.argv[0])
        sys.exit(1)
    project_meta_dict = {"project_name": project_name, "user_name": user_name}
    upload_images_to_s3(project_name)
    s3_project_path = os.path.join(S3_DATA_PATH, project_name)
    send_data_to_injester(s3_project_path, project_meta_dict)
