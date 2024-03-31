"""Under Construction ..."""
"""kafka_consumer.py"""

from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
from json.decoder import JSONDecodeError
from rich import print as rprint
import logging
import ssl
import sys
import json


def kafka_consumer(
    topic_name: str,
    client_id: str,
    consumer_group_id: str,
    bootstrap_servers: list,
    security_protocol: str,
    sasl_mechanism: str,
    sasl_plain_username: str,
    sasl_plain_password: str,
    offset: str = "earliest", # earliest or latest
    value_deserializer=lambda x: json.loads(x.decode("utf-8")),
    key_deserializer=lambda x: json.loads(x.decode("utf-8")) if x is not None else None,
    verify_mode: str = "CERT_NONE", # CERT_OPTIONAL, CERT_REQUIRED
) -> None:
    """
    Consume messages from Kafka topic and log events.

    Args:
        topic_name: Name of the Kafka topic to consume from.
        client_id: Client ID used to identify the consumer.
        consumer_group_id: ID of the consumer group.
        bootstrap_servers: List of Kafka broker addresses.
        auto_offset_reset: Strategy for resetting the offset on startup.
        value_deserializer: Deserializer function for message values.
        key_deserializer: Deserializer function for message keys.
        verify_mode: SSL context verification mode.

    Returns: 
        None
    
    Raises:
        NoBrokersAvailable: Failed to connect to Kafka.
        JSONDecodeError: If an error occurs during JSON decoding of the message value.
        UnicodeError: If an error occurs during decoding of the message value due to Unicode error.
    """

    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Kafka consumer...")
    
    # Create a Kafka consumer
    try:
        consumer = KafkaConsumer(
            topic_name,
            client_id=client_id,
            group_id=consumer_group_id,
            bootstrap_servers=bootstrap_servers,
            auto_offset_reset=offset,
            value_deserializer=value_deserializer,
            key_deserializer=key_deserializer,
            ssl_context=verify_mode,
            security_protocol=security_protocol,
            sasl_mechanism=sasl_mechanism,
            sasl_plain_username=sasl_plain_username,
            sasl_plain_password=sasl_plain_password,
            enable_auto_commit=False
        )
    except NoBrokersAvailable as e:
        logger.error(f"No brokers available: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to connect to Kafka: {e}")
        sys.exit(1)
        
    logger.info("Connected to Kafka.")

    # Continuously poll for messages
    try:
        for message in consumer:
            try:
                event_data = {
                    "event": {
                        "topic": message.topic,
                        "partition": message.partition,
                        "offset": message.offset,
                        "key": message.key,
                        "value": message.value,
                    }
                }
                rprint((event_data))
                
            except (json.JSONDecodeError, UnicodeError) as err:
                logger.error(f"Error processing message: {err}")
                
    except KeyboardInterrupt:
        sys.exit("Exited the program gracefully")
        
    finally:
        consumer.close()
        logger.info("Consumer connection closed.")


if __name__ == "__main__":
    # Example usage
    topic_name = "cisco-telemetry"
    consumer_group_id = "my-macbook-consumer"
    bootstrap_servers = ["devnetbox:9092"]
    client_id = "my-macbook"
    offset = "latest" 

    kafka_consumer(topic_name, 
                   consumer_group_id, 
                   bootstrap_servers, 
                   offset,
                   )