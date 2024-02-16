# API_Gateway/API.py modifications
from network.command_handler import CommandHandler

@app.route('/add_ue', methods=['POST'])
def add_ue():
    data = request.json
    # Validation and logging remain the same
    try:
        CommandHandler.handle_command('add_ue', data)
        return jsonify({'message': 'UE added successfully'}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An error occurred while adding UE'}), 500

@app.route('/remove_ue', methods=['POST'])
def remove_ue():
    data = request.json
    # Validation and logging remain the same
    try:
        CommandHandler.handle_command('remove_ue', data)
        return jsonify({'message': 'UE removed successfully'}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An error occurred while removing UE'}), 500

@app.route('/update_ue', methods=['POST'])
def update_ue():
    data = request.json
    # Validation and logging remain the same
    try:
        CommandHandler.handle_command('update_ue', data)
        return jsonify({'message': 'UE updated successfully'}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An error occurred while updating UE'}), 500