from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    sensor_id = db.Column(db.String(64), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    value1 = db.Column(db.Float, nullable=False)
    value2 = db.Column(db.Float)
    value3 = db.Column(db.Float)
    value4 = db.Column(db.Float)
    value5 = db.Column(db.Float)
    value6 = db.Column(db.Float)
    unit1 = db.Column(db.String(10))
    unit2 = db.Column(db.String(10))
    unit3 = db.Column(db.String(10))
    unit4 = db.Column(db.String(10))
    unit5 = db.Column(db.String(10))
    unit6 = db.Column(db.String(10))

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
