# %% IMPORTS

import typing as T

import pydantic as pdt

from autogen_team.core import schemas
from autogen_team.io import kafka
from autogen_team.jobs import base
import pandas as pd

# %% JOBS

class KafkaInferenceJob(base.Job):
    """Generate batch predictions using Kafka streams for inputs and outputs.

    Parameters:
        input_topic (str): Kafka topic for input data.
        output_topic (str): Kafka topic for output data.
        alias_or_version (str | int): Alias or version for the model.
        loader (kafka.LoaderKind): Registry loader for the model.
        kafka_config (dict): Kafka configuration settings.
    """

    KIND: T.Literal["KafkaInferenceJob"] = "KafkaInferenceJob"

    # Kafka topics
    input_topic: str
    output_topic: str

    # Model
    alias_or_version: str | int = "Champion"

    # Loader
    loader: kafka.LoaderKind = pdt.Field(kafka.CustomLoader(), discriminator="KIND")

    # Kafka config
    kafka_config: dict = {}

    @T.override
    def run(self) -> base.Locals:
        # services
        logger = self.logger_service.logger()
        logger.info("Starting Kafka Inference Job")

        # Initialize Kafka producer and consumer
        logger.info("Connecting to Kafka...")
        consumer = kafka.create_consumer(self.input_topic, self.kafka_config)
        producer = kafka.create_producer(self.kafka_config)
        logger.info("Kafka connected: input_topic={}, output_topic={}", self.input_topic, self.output_topic)

        # model
        logger.info("With model: {}", self.mlflow_service.registry_name)
        model_uri = kafka.uri_for_model_alias_or_version(
            name=self.mlflow_service.registry_name, alias_or_version=self.alias_or_version
        )
        logger.debug("- Model URI: {}", model_uri)

        logger.info("Load model: {}", self.loader)
        model = self.loader.load(uri=model_uri)
        logger.debug("- Model: {}", model)

        # Process messages
        logger.info("Listening for messages on input topic: {}", self.input_topic)
        for message in consumer:
            logger.debug("Received message: {}", message)
            inputs_ = pd.DataFrame([message.value])  # Assume JSON input is converted to DataFrame
            inputs = schemas.InputsSchema.check(inputs_)

            logger.info("Predict outputs")
            outputs = model.predict(inputs=inputs)  # checked
            logger.debug("- Outputs: {}", outputs)

            # Send predictions to output topic
            logger.info("Sending predictions to output topic: {}", self.output_topic)
            producer.send(self.output_topic, outputs.to_json())
            producer.flush()

            # Log and notify
            logger.info("Processed message successfully.")
            self.alerts_service.notify(
                title="Kafka Inference Job Processed Message", 
                message=f"Input Topic: {self.input_topic}, Output Topic: {self.output_topic}"
            )

        return locals()
