import pika
import pickle
import os, shutil
from configurations import S3_DATA_PATH, EXTERNAL_RABBITMQ_HOST


def copy_result(source_path, dest_path):
    shutil.copy(source_path, dest_path)


def upload_result_to_s3(result_file_path, project_meta_dict):
    result_file_name = project_meta_dict["version_result_name"]
    dest_path = S3_DATA_PATH
    os.makedirs(dest_path, exist_ok=True)
    copy_result(result_file_path, dest_path)
    return os.path.join(S3_DATA_PATH, result_file_name)


def send_result_to_ext_consumers(result_file_path, project_meta_dict):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=EXTERNAL_RABBITMQ_HOST)
    )
    channel = connection.channel()
    channel.exchange_declare(exchange="ext_consumer", exchange_type="topic")
    routing_key = project_meta_dict["project_name"]
    s3_result_path = upload_result_to_s3(result_file_path, project_meta_dict)
    message = pickle.dumps((s3_result_path))
    channel.basic_publish(
        exchange="ext_consumer", routing_key=routing_key, body=message
    )
    print(" [x] Sent %r:%r" % (routing_key, message))
    connection.close()


def callback(ch, method, properties, body):
    print(" [x] %r" % body)
    # ch.basic_ack(delivery_tag=method.delivery_tag)
    result_file_path, project_meta_dict = pickle.loads(body)
    print("*******", result_file_path, project_meta_dict)
    send_result_to_ext_consumers(result_file_path, project_meta_dict)


print(" [*] Waiting for data from Enricher. To exit press CTRL+C")
if __name__ == "__main__":
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
    channel = connection.channel()
    channel.exchange_declare(exchange="consumer", exchange_type="fanout")
    result = channel.queue_declare(queue="", exclusive=True)
    queue_name = result.method.queue

    channel.queue_bind(exchange="consumer", queue=queue_name)
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()
