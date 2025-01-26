import json
import paho.mqtt.client as mqtt
import time

class LogistixRequester:
    def __init__(self):
        self.config = self.load_config()
        self.client = mqtt.Client()
        self.setup_mqtt()
        self.response_received = False
        
    def load_config(self):
        with open('config.json', 'r') as f:
            return json.load(f)
            
    def setup_mqtt(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
        broker = self.config['broker']['mqttbroker']
        port = self.config['broker']['port']
        self.client.connect(broker, port, 60)
        
    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code {rc}")
        # Subscribe to response topic
        topic = self.config['contractor']['topics']['publishing']
        self.client.subscribe(topic)
        
    def on_message(self, client, userdata, msg):
        try:
            response = json.loads(msg.payload.decode())
            print("\nReceived response:")
            print(json.dumps(response, indent=2))
            self.response_received = True
        except json.JSONDecodeError:
            print("Invalid JSON response received")
        except Exception as e:
            print(f"Error processing response: {e}")
            
    def send_request(self):
        # Create sample request
        request = {
            "key": self.config['contractor']['key'],
            "contractcode": "pip-tqdm",
            "contractdesc": "send me the package in zip format",
            "shipment-type": "zip",
            "agent": {
                "model": "pip_binary_v01.py",
                "parameters": {
                    "platform": "win_amd64",
                    "python-version": "3.12",
                    "package": "tqdm"
                }
            }
        }
        
        # Send request
        topic = self.config['contractor']['topics']['subscription']
        print("\nSending request:")
        print(json.dumps(request, indent=2))
        self.client.publish(topic, json.dumps(request))
        
    def run(self):
        # Start the MQTT client loop in a non-blocking way
        self.client.loop_start()
        
        # Wait for connection
        time.sleep(1)
        
        # Send the request
        self.send_request()
        
        # Wait for response with timeout
        timeout = 30  # seconds
        start_time = time.time()
        while not self.response_received and time.time() - start_time < timeout:
            time.sleep(0.1)
            
        if not self.response_received:
            print("\nTimeout: No response received")
            
        # Stop the MQTT client loop
        self.client.loop_stop()
        self.client.disconnect()

if __name__ == "__main__":
    requester = LogistixRequester()
    requester.run() 