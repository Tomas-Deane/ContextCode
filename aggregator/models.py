from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import CheckConstraint, UniqueConstraint

db = SQLAlchemy()

class Device(db.Model):
    __tablename__ = 'device'
    id = db.Column(db.Integer, primary_key=True)
    guid = db.Column(db.String(36), unique=True, nullable=False)  # Server-assigned GUID
    friendly_name = db.Column(db.String(50), nullable=True)
    type = db.Column(db.String(50), nullable=False)  # e.g., "PC-Metrics", "OpenSky-Collector"
    metrics = db.relationship('Metric', backref='device', lazy=True)
    commands = db.relationship('Command', backref='device', lazy=True)

class Metric(db.Model):
    __tablename__ = 'metric'
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    readings = db.relationship('Reading', backref='metric', lazy=True)
    # Define field definitions for this metric (up to 5 fields)
    metric_fields = db.relationship('MetricField', backref='metric', lazy=True)

class MetricField(db.Model):
    __tablename__ = 'metric_field'
    id = db.Column(db.Integer, primary_key=True)
    metric_id = db.Column(db.Integer, db.ForeignKey('metric.id'), nullable=False)
    field_index = db.Column(db.Integer, nullable=False)
    field_name = db.Column(db.String(50), nullable=False)
    field_type = db.Column(db.String(20), nullable=False)  # e.g., 'numeric', 'string'
    __table_args__ = (
        UniqueConstraint('metric_id', 'field_index', name='uq_metric_field_index'),
        CheckConstraint('field_index BETWEEN 1 AND 5', name='ck_field_index_range')
    )

class Reading(db.Model):
    __tablename__ = 'reading'
    id = db.Column(db.Integer, primary_key=True)
    metric_id = db.Column(db.Integer, db.ForeignKey('metric.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    # Each reading may have multiple field values defined in the metric_field table
    reading_values = db.relationship('ReadingValue', backref='reading', lazy=True)

class ReadingValue(db.Model):
    __tablename__ = 'reading_value'
    id = db.Column(db.Integer, primary_key=True)
    reading_id = db.Column(db.Integer, db.ForeignKey('reading.id'), nullable=False)
    metric_field_id = db.Column(db.Integer, db.ForeignKey('metric_field.id'), nullable=False)
    value = db.Column(db.String(255), nullable=False)
    __table_args__ = (
        UniqueConstraint('reading_id', 'metric_field_id', name='uq_reading_metric_field'),
    )
    # Define the relationship to MetricField
    metric_field = db.relationship('MetricField', lazy=True)

class Command(db.Model):
    __tablename__ = 'command'
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=False)
    command_text = db.Column(db.String(100), nullable=False)
    executed = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
