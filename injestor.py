import pika
import pickle
import os, shutil
from db_helper import get_latest_project_version
import time
import multiprocessing as mp
from configurations import PROJECT_FOLDER, EXTERNAL_RABBITMQ_HOST


def copy_image(source_path, dest_path):
    shutil.move(source_path, dest_path)


def get_images_from_s3(s3_project_path, project_meta_dict):
    """
    this function is used to send images to enricher after getting them form s3/local storage
    """
    # s3_project_path = os.path.join(
    #     "/Users/dkm/", s3_project_path
    # )  # only when testing locally
    images_list = os.listdir(s3_project_path)
    project_name = project_meta_dict["project_name"]
    latest_version = project_meta_dict["latest_version"]
    dest_folder = os.path.join(PROJECT_FOLDER, project_name, latest_version)
    os.makedirs(dest_folder, exist_ok=True)
    time.sleep(5)
    for image in images_list:
        source_path = os.path.join(s3_project_path, image)
        dest_path = os.path.join(dest_folder, image)
        copy_image(source_path, dest_path)
    latest_version_path = os.path.join(PROJECT_FOLDER, project_name, latest_version)
    send_message_to_enricher(latest_version_path, project_meta_dict)


def send_message_to_enricher(latest_version_path, project_meta_dict):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
    channel = connection.channel()
    channel.exchange_declare(exchange="enricher", exchange_type="fanout")
    message = pickle.dumps((latest_version_path, project_meta_dict))
    channel.basic_publish(exchange="enricher", routing_key="", body=message)
    print(" [x] Sent %r" % message)
    connection.close()


def callback(ch, method, properties, body):
    print(" [x] %r" % body)
    # ch.basic_ack(delivery_tag=method.delivery_tag)
    s3_project_path, project_meta_dict = pickle.loads(body)
    print("*******", s3_project_path, project_meta_dict)
    project_name = project_meta_dict["project_name"]
    user = project_meta_dict["user_name"]
    project_meta_dict["project_name_folder"] = os.path.join(
        PROJECT_FOLDER, project_name
    )
    latest_version = get_latest_project_version(user, project_name)
    project_meta_dict["latest_version"] = latest_version
    p = mp.Process(target=get_images_from_s3, args=(s3_project_path, project_meta_dict))
    p.start()


print("Waiting for data from image_pusher. To exit press CTRL+C")
if __name__ == "__main__":
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=EXTERNAL_RABBITMQ_HOST)
    )
    channel = connection.channel()
    channel.exchange_declare(exchange="injestor", exchange_type="fanout")
    result = channel.queue_declare(queue="", exclusive=True)
    queue_name = result.method.queue

    channel.queue_bind(exchange="injestor", queue=queue_name)
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()
