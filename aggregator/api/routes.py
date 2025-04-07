import uuid
from flask import Blueprint, request, jsonify, render_template, current_app
from aggregator.models import db, Device
from aggregator.services.metrics_service import process_metrics
from aggregator.services.metrics_query_service import get_latest_metrics
from aggregator.services.history_service import get_metric_history
from aggregator.services.schema_service import get_schema
from aggregator.services.command_service import send_device_command, get_pending_commands

api_bp = Blueprint('api_bp', __name__)

@api_bp.route('/')
def index():
    return render_template('dashboard.html')

@api_bp.route('/api/metrics', methods=['GET', 'POST'])
def metrics():
    """
    GET: Return the latest reading for each metric.
    POST: Receives metrics from a collector.
    Expects JSON with 'device_guid' and 'metrics' (a list of metric objects).
    """
    if request.method == 'GET':
        metrics_data = get_latest_metrics()
        return jsonify(metrics_data)
    elif request.method == 'POST':
        api_key = request.headers.get('X-API-Key')
        if api_key != current_app.config.get('API_KEY'):
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json()
        device_guid = data.get('device_guid')
        metrics_list = data.get('metrics')

        if not device_guid or not metrics_list:
            return jsonify({"error": "device_guid and metrics are required"}), 400

        device = Device.query.filter_by(guid=device_guid).first()
        if not device:
            return jsonify({'error': 'Device not registered'}), 404

        process_metrics(device, metrics_list)
        return jsonify({"status": "ok"}), 200

@api_bp.route('/api/history/<int:metric_id>', methods=['GET'])
def history(metric_id):
    """
    Return historical readings for a given metric with pagination.
    """
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    history_data = get_metric_history(metric_id, page, page_size)
    return jsonify(history_data)

@api_bp.route('/api/command', methods=['POST'])
def send_command():
    """
    Endpoint to send a command to a device.
    Expects JSON with keys 'device' and 'command'.
    """
    data = request.get_json()
    device_friendly = data.get('device')
    command_text = data.get('command')
    if not device_friendly or not command_text:
        return jsonify({"error": "Device and command are required"}), 400
    command, err = send_device_command(device_friendly, command_text)
    if err:
        # return error if command sending failed
        return jsonify({"error": err}), 404
    return jsonify({"status": "Command sent", "command_id": command.id})

@api_bp.route('/api/command/<friendly_name>', methods=['GET'])
def get_commands(friendly_name):
    """
    Endpoint to retrieve pending commands for a device.
    """
    commands, err = get_pending_commands(friendly_name)
    if err:
        # return error if device not found
        return jsonify({"error": err}), 404
    return jsonify(commands)

@api_bp.route('/api/register', methods=['POST'])
def register_device():
    """
    Registers a new device.
    Expects JSON with 'role' and 'friendly_name'.
    """
    data = request.get_json()
    role = data.get("role")
    friendly_name = data.get("friendly_name")
    if not role or not friendly_name:
        return jsonify({"error": "role and friendly_name are required"}), 400

    new_guid = str(uuid.uuid4())
    new_device = Device(guid=new_guid, friendly_name=friendly_name, type=role)
    db.session.add(new_device)
    db.session.commit()
    return jsonify({"device_guid": new_guid, "friendly_name": friendly_name, "type": role}), 201

@api_bp.route('/api/schema', methods=['GET'])
def schema():
    """
    Returns the current schema: a list of devices with their metrics and field definitions.
    """
    schema_data = get_schema()
    return jsonify(schema_data)