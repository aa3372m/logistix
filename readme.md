# Logistix

Logistix is to facilitate remote task execution through MQTT communication. It uses MQTT to enable agents to perform tasks remotely and efficiently, returning results to the requester in real-time. The application listens for incoming requests, processes them, and executes specified agents, ensuring that the results are promptly published back to a designated MQTT topic. This makes Logistix an ideal solution for distributed systems requiring seamless and reliable task management and execution.


## Features

- **MQTT Communication**: Connects to an MQTT broker to subscribe to a topic for incoming requests and publishes responses to another topic.
- **Request Processing**: Validates incoming requests and executes specified agents.
- **Agent Execution**: Runs Python scripts (agents) based on the request and handles their output.
- **Error Handling**: Provides error messages for invalid JSON, missing agents, and failed agent executions.

## Configuration

The application is configured using a `config.json` file. Below is an example configuration:
