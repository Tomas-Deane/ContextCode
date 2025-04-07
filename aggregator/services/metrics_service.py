from aggregator.models import db, Metric, MetricField, Reading, ReadingValue

def process_metrics(device, metrics_list):
    """
    Process a list of metrics for the given device.
    
    For each metric in the list:
      - If the metric does not exist, create it and define its fields.
      - If it exists, check for new fields and add them if needed.
      - Create a new reading and record the reading values.
    """
    for metric_data in metrics_list:
        metric_name = metric_data.get('name')
        fields_data = metric_data.get('fields')
        if not metric_name or not fields_data:
            continue  # Skip invalid metric data

        # Check if the metric exists for this device.
        metric = Metric.query.filter_by(device_id=device.id, name=metric_name).first()
        if not metric:
            # Create a new metric.
            metric = Metric(device_id=device.id, name=metric_name)
            db.session.add(metric)
            db.session.commit()  # Commit to obtain metric.id

            # Create field definitions based on incoming data.
            index = 1
            for field_name, field_value in fields_data.items():
                field_type = 'numeric' if isinstance(field_value, (int, float)) else 'string'
                mf = MetricField(
                    metric_id=metric.id,
                    field_index=index,
                    field_name=field_name,
                    field_type=field_type
                )
                db.session.add(mf)
                index += 1
            db.session.commit()
        else:
            # Metric exists—check for any new fields.
            existing_field_names = {mf.field_name for mf in metric.metric_fields}
            next_index = len(metric.metric_fields) + 1
            for field_name, field_value in fields_data.items():
                if field_name not in existing_field_names and next_index <= 5:
                    field_type = 'numeric' if isinstance(field_value, (int, float)) else 'string'
                    mf = MetricField(
                        metric_id=metric.id,
                        field_index=next_index,
                        field_name=field_name,
                        field_type=field_type
                    )
                    db.session.add(mf)
                    next_index += 1
            db.session.commit()

        # Create a new Reading for the metric.
        reading = Reading(metric_id=metric.id)
        db.session.add(reading)
        db.session.commit()

        # Record a ReadingValue for each defined field if provided.
        for mf in metric.metric_fields:
            if mf.field_name in fields_data:
                rv = ReadingValue(
                    reading_id=reading.id,
                    metric_field_id=mf.id,
                    value=str(fields_data[mf.field_name])
                )
                db.session.add(rv)
        db.session.commit()
