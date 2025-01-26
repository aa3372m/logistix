import json
import os
import paho.mqtt.client as mqtt
import subprocess
from pathlib import Path

class Logistix:
    def __init__(self):
        self.config = self.load_config()
        self.client = mqtt.Client()
        self.setup_mqtt()

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
        topic = self.config['contractor']['topics']['subscription']
        self.client.subscribe(topic)

    def on_message(self, client, userdata, msg):
        try:
            request = json.loads(msg.payload.decode())
            self.process_request(request)
        except json.JSONDecodeError:
            print("Invalid JSON received")
        except Exception as e:
            print(f"Error processing message: {e}")

    def process_request(self, request):
        # Verify contractor key
        if request.get('key') != self.config['contractor']['key']:
            print("Invalid contractor key")
            return

        # Create contract directory
        contract_dir = Path('contracts') / request['key'] / request['contractcode']
        contract_dir.mkdir(parents=True, exist_ok=True)

        # Save request
        request_file = contract_dir / 'request.json'
        
        # Check if agent exists
        agent_path = Path('agents') / request['agent']['model']
        if not agent_path.exists():
            response = {
                "error": "agent not found"
            }
            self.save_response(contract_dir, response)
            self.publish_response(response)
            return

        # Prepare request for agent
        agent_request = {
            "key": request['key'],
            "contractcode": request['contractcode'],
            "agent": request['agent']['model'],
            "status": "running",
            "parameters": request['agent']['parameters']
        }

        # Save updated request
        with open(request_file, 'w') as f:
            json.dump(agent_request, f, indent=2)

        # Run agent
        try:
            subprocess.run(['python', str(agent_path), str(request_file)], check=True)
            
            # Read response
            with open(contract_dir / 'response.json', 'r') as f:
                response = json.load(f)
                self.publish_response(response)
        except subprocess.CalledProcessError as e:
            print(f"Agent execution failed: {e}")
            response = {
                "error": "agent execution failed"
            }
            self.save_response(contract_dir, response)
            self.publish_response(response)

    def save_response(self, contract_dir, response):
        with open(contract_dir / 'response.json', 'w') as f:
            json.dump(response, f, indent=2)

    def publish_response(self, response):
        topic = self.config['contractor']['topics']['publishing']
        self.client.publish(topic, json.dumps(response))

    def run(self):
        self.client.loop_forever()

if __name__ == "__main__":
    logistix = Logistix()
    logistix.run() 