# Prediction Service Microservice

## Overview

This repository houses the Prediction Service, a microservice architected using FastAPI. It adopts clean architecture and Domain-Driven Design (DDD) patterns to asynchronously process prediction requests. The requests are queued in RabbitMQ, processed by TorchServe workers, and the results are stored in Redis for subsequent retrieval.

Designed for scalability and robustness, it can manage a high volume of requests through asynchronous processing, rate limiting for TorchServe client requests, and detailed logging and error handling mechanisms.

## High-Level Functionality

- **Prediction Requests**: Clients submit prediction tasks through an API endpoint, which publishes these tasks to a RabbitMQ queue.
- **Task Processing**: Background workers process the queued tasks using TorchServe.
- **Result Storage**: Results are stored in Redis with a unique inference ID.
- **Result Retrieval**: Clients can fetch the prediction results using the inference ID through a specific API endpoint.

## Architecture Enhancements

The architecture has been enhanced for improved performance and reliability:

- **RabbitMQ Asynchronous Handling**: Upgraded the RabbitMQ consumer for better asynchronous task handling, with concurrency and acknowledgement mechanisms for dependable processing.
- **Rate Limiter for TorchServe Client**: A rate limiter has been integrated to manage TorchServe load and ensure balanced resource use.
- **Timeout and Cancellation**: Introduced features for managing long-running prediction tasks, including timeout settings and task cancellation.
- **Logging**: The logging system has been improved for detailed insights into the prediction request lifecycle, aiding in monitoring and troubleshooting.

## Schematic Flow

The service interactions follow this schematic flow:

```plaintext
  +-------+           +--------+           +-----------+
  |       |           |        |           |           |
  | User  +-----------> FastAPI+-----------> RabbitMQ  |
  |       |           |        |           |           |
  +---+---+           +----+---+           +-----+-----+
      |                    |                     |
      |                    |                     |
      |                    v                     |
      |                +---+----+                |
      |                | Redis  |                |
      |                +---+----+                |
      |                    ^                     |
      |                    |                     |
      |                    |                     v
      |                +---+----+         +------+------+
      |                |        |         |             |
      +---------------->        <---------+ TorchServe  |
                       |        |         | Worker(s)   |
                       +--------+         +-------------+
  ```

## Technical Challenges and Solutions

### RabbitMQ Integration

- **Challenge**: Stability with RabbitMQ connections and message delivery was problematic.
- **Solution**: Utilized the **backoff** library for reconnection strategies and **aio_pika** for asynchronous message processing.

### Worker Service Containerization

- **Challenge**: Constructing a scalable, resilient worker container.
- **Solution**: Leveraged Docker for containerization, with an optimized Dockerfile for lightweight, efficient scalability.

### Retrieving Output in Various Formats from Torch Serve

- **Challenge**: Handling varied output formats from TorchServe predictions.
- **Solution**: The TorchServe client was made format-agnostic, capable of handling diverse content types, enhancing client application integration (**magic** library helped).

### Dependency Injection

- Utilized FastAPI's dependency injection system to manage configurations and shared resources, resulting in cleaner code and simpler testing procedures.

## Project Enhancements

- **Scripts**: Added utility scripts for environment setup, service initialization, and deployment tasks.
- **Logging Enhancements**:  Implemented structured logging for better log analysis and issue diagnosis.
- **Swagger Documentation**: The documentation now includes thorough endpoint descriptions, input/output details, and example error responses.

## Getting Started

- To begin using the Prediction Service, ensure you have a pretrained [Fast-RCNN model](https://github.com/pytorch/serve/tree/master/examples/object_detector/fast-rcnn) and create a model archive file to place in the `./model-store` directory.
- Make sure Docker is installed on your system, then run:

```sh
docker-compose up
```

You can access the enhanced prediction controller via: <http://localhost:8002/api/predictions/docs>.

## Project Structure

```
│   Dockerfile
│   requirements.txt
│
├───app
│   │   ...
│   ├───api
│   │   ...
│   ├───core
│   │   ...
│   ├───domain
│   │   ...
│   ├───infrastructure
│   │   ...
│   ├───middleware
│   │   ...
│   └───schemas
│       ...
├───logs
│   ...
├───scripts
│   ...
└───worker
    ...
```

The tree above represents the directory structure of the project, with each component encapsulated within its respective module, following clean architecture principles.

## Request examples
- Predictions request body:
  ```json
  {
    "prediction_model_name": "fastrcnn",
    "image_path": "/images/cat.jpg"
  }
  ```

## Response examples

- Success file response format from TorchServe:
![File response success](https://i.ibb.co/hWZ1QVM/image.png)

- Success json response format from TorchServe:
  ```json
    {
    "prediction_model_name": "example_model",
    "results": [
        {
        "label": "cat",
        "score": 0.9
        }
    ]
    }
  ```

- Pending json response format from TorchServe:
  ```json
    {
    "prediction_model_name": "example_model",
    "results": "Pending"
    }
  ```

- Pending json response format from TorchServe:
  ```json
    {
    "prediction_model_name": "example_model",
    "results": "Error while making the prediction"
    }
  ```

## References

For further understanding of this service's implementation, a reference guide is available that inspired some of the architectural decisions:

- [Running PyTorch models for inference using FastAPI, RabbitMQ, Redis & Docker](https://www.auroria.io/running-pytorch-models-for-inference-using-fastapi-rabbitmq-redis-docker/)

## Conclusion

The Prediction Service microservice is a robust and efficient system designed for scalable machine learning inference tasks. Through the use of FastAPI, RabbitMQ, Redis, and Docker, it ensures high availability and responsiveness for clients requesting prediction services.