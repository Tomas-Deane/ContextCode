from aggregator.models import Device

def get_schema():
    """
    Returns the current schema as a list of devices.
    Each device includes its metrics and each metric its field definitions.
    """
    devices = Device.query.all()
    schema = []
    for device in devices:
        device_entry = {
            "friendly_name": device.friendly_name,
            "type": device.type,
            "metrics": []
        }
        for metric in device.metrics:
            metric_entry = {
                "name": metric.name,
                "metric_id": metric.id,
                "fields": []
            }
            for mf in metric.metric_fields:
                metric_entry["fields"].append({
                    "field_index": mf.field_index,
                    "field_name": mf.field_name,
                    "field_type": mf.field_type
                })
            device_entry["metrics"].append(metric_entry)
        schema.append(device_entry)
    return schema
