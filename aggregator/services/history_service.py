from aggregator.models import Reading
from collections import OrderedDict

def get_metric_history(metric_id, page, page_size):
    """
    Retrieve historical readings for a given metric with pagination.
    Returns a dictionary with pagination info and a list of history records.
    """
    query = Reading.query.filter_by(metric_id=metric_id).order_by(Reading.timestamp.desc())
    pagination = query.paginate(page, page_size, error_out=False)

    history = []
    for r in pagination.items:
        # sort reading values by field index
        sorted_rvs = sorted(r.reading_values, key=lambda rv: rv.metric_field.field_index)
        ordered_fields = OrderedDict()
        for rv in sorted_rvs:
            # add field name and value to ordered dictionary
            ordered_fields[rv.metric_field.field_name] = rv.value
        history.append({
            'timestamp': r.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            'fields': ordered_fields
        })

    return {
        'page': page,
        'page_size': page_size,
        'total': pagination.total,
        'pages': pagination.pages,
        'history': history
    }
