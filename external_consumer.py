import pika
import sys
import pickle

connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
channel = connection.channel()

channel.exchange_declare(exchange="ext_consumer", exchange_type="topic")

result = channel.queue_declare("", exclusive=True)
queue_name = result.method.queue

binding_keys = sys.argv[1:]
if not binding_keys:
    sys.stderr.write("Usage: %s [binding_key]...\n" % sys.argv[0])
    sys.exit(1)

for binding_key in binding_keys:
    channel.queue_bind(
        exchange="ext_consumer", queue=queue_name, routing_key=binding_key
    )

print("[*] Waiting for changes in %s To exit press CTRL+C" % binding_keys)


def callback(ch, method, properties, body):
    print(" [x] %r:%r" % (method.routing_key, body))
    # ch.basic_ack(delivery_tag=method.delivery_tag)
    result_file_path = pickle.loads(body)
    print("*******", result_file_path)


channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
channel.start_consuming()
