from aggregator.models import Metric, Reading

def get_latest_metrics():
    """
    Retrieve the latest reading for each metric and return a list of dictionaries
    with aggregated metric data.
    """
    metrics_data = []
    metrics = Metric.query.all()
    for metric in metrics:
        latest_reading = Reading.query.filter_by(metric_id=metric.id)\
                                      .order_by(Reading.timestamp.desc())\
                                      .first()
        if latest_reading:
            fields = {}
            for rv in latest_reading.reading_values:
                # add field name and value to fields dictionary
                fields[rv.metric_field.field_name] = rv.value
            metrics_data.append({
                'device': metric.device.friendly_name,
                'metric': metric.name,
                'fields': fields,
                'timestamp': latest_reading.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                'metric_id': metric.id
            })
    return metrics_data
