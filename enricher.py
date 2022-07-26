import pika
import pickle
import os
import multiprocessing as mp
import time
from configurations import RABBITMQ_HOST


def create_result_file(latest_version_path, project_meta_dict):
    """
    we are just creating a list of latest project files and storing them in a file and sending it
    """
    images_list = os.listdir(latest_version_path)
    version_result = project_meta_dict["version_result_name"]
    result_path = os.path.join(project_meta_dict["project_name_folder"], version_result)
    f = open(result_path, "a")
    f.write(str(images_list))
    f.close()
    time.sleep(10)

    result_file_path = os.path.join(
        project_meta_dict["project_name_folder"],
        project_meta_dict["latest_version"] + "_result",
    )
    send_result_to_consumer(result_file_path, project_meta_dict)


def send_result_to_consumer(result_file_path, project_meta_dict):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.exchange_declare(exchange="consumer", exchange_type="fanout")
    message = pickle.dumps((result_file_path, project_meta_dict))
    channel.basic_publish(exchange="consumer", routing_key="", body=message)
    print(" [x] Sent %r" % message)
    connection.close()


def callback(ch, method, properties, body):
    print(" [x] %r" % body)
    # ch.basic_ack(delivery_tag=method.delivery_tag)
    latest_version_path, project_meta_dict = pickle.loads(body)
    print("*******", latest_version_path, project_meta_dict)
    version_result = project_meta_dict["latest_version"] + "_result"
    project_meta_dict["version_result_name"] = version_result
    p = mp.Process(
        target=create_result_file, args=(latest_version_path, project_meta_dict)
    )
    p.start()


print(" [*] Waiting for data from Injestor. To exit press CTRL+C")
if __name__ == "__main__":
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.exchange_declare(exchange="enricher", exchange_type="fanout")
    result = channel.queue_declare(queue="", exclusive=True)
    queue_name = result.method.queue

    channel.queue_bind(exchange="enricher", queue=queue_name)
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()
