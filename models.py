from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime
db = SQLAlchemy()
import base64

class Documents(db.Model, SerializerMixin):
    __tablename__ = 'documents'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    document = db.Column(db.LargeBinary, nullable=False)
    type = db.Column(db.String(255), nullable=False)
    date_created = db.Column(db.DateTime, unique=False, nullable=False, default=datetime.utcnow)
    description = db.Column(db.String(255), nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'date_created': self.date_created.isoformat(),
            'description': self.description,
            'document': base64.b64encode(self.document).decode('utf-8')
        }