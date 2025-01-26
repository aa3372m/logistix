# Logistix

Assist me in developing a project called logistix that takes a contract in json, perform tasks, and responds as per the agreed shipment-type e.g., json, text, zip.

## Release 1.0.0

- create app.py in python 3.12 based project using compatible libraries like paho-mqtt, json, etc. 
- create project structure as config.json, app.py. agents directory has python scripts as agents e.g., pip_binary_v01.py . directories as contracts (based on contractor key). for each request it creates a subdirectory  with contractcode (eg. "pip-tqdm") and two files as request.json and response.json. request.json has the request (received from the subscribed topic) and response (published/tobe published on publishing topic). based on the request's shipment-type additional files and folders may also be created in the subdirectory. zip and sending the zip file is also possible.
- config.json file to store the configuration
e.g.
```json

{
"broker": {
    "mqttbroker": "broker.hivemq.com",
    "port": 1883
  },
  "contractor": {
    "key": "asimkhan",
    "topics": {
      "subscription": "request",
      "publishing": "response"
    }
  }
}
```

Sameple scenation:
1) we have the following config.json that is loaded by app.py

```json

{
"broker": {
    "mqttbroker": "broker.hivemq.com",
    "port": 1883
  },
  "contractor": {
    "key": "asimkhan",
    "topics": {
      "subscription": "request",
      "publishing": "response"
    }
  }
}
```

2) app.py loads the config.json and subscribes to the request topic. 

3) The following is the request received from the request topic:
```json
{
    "key": "asimkhan",
    "contractcode": "pip-tqdm",
    "contractdesc": "send me the package in zip format",
    "shipment-type": "zip",
    "agent": {"model": "pip_binary_v01.py", "parameters": {"platform": "win_amd64",  "python-version": "3.12", "package": "tqdm"}}
}
```
4) it checks if key matches with the contractor key in config.json. if not, it ignores the request.
5) creates a subdirectory with the contractcode and the request.json file in it.
6) check of agent exists in the agents directory. if not, it ignores the request and writes the error to the response.json file. ({"error": "agent not found"})
7) if agent exists, the write/replace the request.json file 
   ```json
{
   "key": "asimkhan",
   "contractcode": "pip-tqdm",
   "agent":"pip_binary_v01.py",
   "status": "running",
   "parameters": {"platform": "win_amd64",  "python-version": "3.12", "package": "tqdm"}
}
```
8) calls the python script (e.g., pip_binary_v01.py) by passing the parameters in json format. i.e., pytthon ./agents/pip_binary_v01.py ./contracts/asimkhan/pip-tqdm/request.json.
9) for agetnt pip_binary_v01.py write the following code:
  a. read the request.json file and focus on the parameters.
  b. create a subdirectory with the name of the package
  c. download the package from the internet and save it in the subdirectory (pip download --platform win_amd64 --only-binary=:all: --python-version 3.12 tqdm).
  d. zip the subdirectory and save it in the subdirectory.
  e. write the response to the response.json file.
   ```json
{
   "key": "asimkhan",
   "contractcode": "pip-tqdm",
   "agent":"pip_binary_v01.py",
   "status": "done",
   "parameters": {"platform": "win_amd64",  "python-version": "3.12", "package": "tqdm"},
   "output": "zip has sent to your email"
}
```