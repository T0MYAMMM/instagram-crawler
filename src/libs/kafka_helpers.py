from kafka import KafkaProducer
from kafka.errors import KafkaError
from config.settings import KAFKA
from .logger import printinfo
import json

def json_deserializer(data):
    return json.loads(data.decode("utf-8"))

def json_serializer(data):
    return json.dumps(data).encode("utf-8")

def publish_kafka(topic, data):
    producer = None
    producer = KafkaProducer(
        bootstrap_servers=KAFKA['default']['bootstrap_servers'],
        value_serializer=json_serializer)
    future = producer.send(topic, data)
    try:
        record_metadata = future.get(timeout=10)
        printinfo('Topic: {};Partition: {};Offset: {}'.format(
            record_metadata.topic, record_metadata.partition, record_metadata.offset
        ))
        return True
    except KafkaError as e:
        # Decide what to do if produce request failed...
        raise
    except Exception as e:
        raise
    finally:
        if producer:
            producer.close()