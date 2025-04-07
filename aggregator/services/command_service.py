from aggregator.models import db, Device, Command
from datetime import datetime, timedelta

def send_device_command(device_friendly, command_text):
    """
    Send a command to a device with safeguards:
      - Do not add a new command if there is already a pending (unexecuted) command.
      - Enforce a time limit of 3 minutes between executing commands.
    """
    device = Device.query.filter_by(friendly_name=device_friendly).first()
    if not device:
        return None, "Device not found"
    
    # Check for existing pending (unexecuted) commands for this device.
    pending_command = Command.query.filter_by(device_id=device.id, executed=False).first()
    if pending_command:
        return None, "A command is already pending for this device. Please wait until it is executed."
    
    # Check when the last executed command was issued (timestamp).
    last_command = (
        Command.query.filter_by(device_id=device.id, executed=True)
        .order_by(Command.timestamp.desc())
        .first()
    )
    if last_command:
        elapsed = datetime.utcnow() - last_command.timestamp
        if elapsed < timedelta(minutes=3):
            return None, "A command was executed less than 3 minutes ago. Please wait before sending a new command."

    # All safeguards passed: add the new command.
    new_command = Command(device_id=device.id, command_text=command_text)
    db.session.add(new_command)
    db.session.commit()
    # return new command and None error
    return new_command, None

def get_pending_commands(device_friendly):
    """
    Retrieve pending commands for a given device and mark them as executed.
    """
    device = Device.query.filter_by(friendly_name=device_friendly).first()
    if not device:
        return None, "Device not found"
    commands = Command.query.filter_by(device_id=device.id, executed=False).all()
    response = []
    for cmd in commands:
        response.append({
            'id': cmd.id,
            'command': cmd.command_text,
            'timestamp': cmd.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        })
        cmd.executed = True
    db.session.commit()
    return response, None
