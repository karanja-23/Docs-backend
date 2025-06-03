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
class User(db.Model, SerializerMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    contact = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    date_created = db.Column(db.DateTime, unique=False, nullable=True, default=datetime.utcnow)
    
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'contact': self.contact,
            'password': self.password
        }
        
class Projects(db.Model, SerializerMixin):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    date_created = db.Column(db.DateTime, unique=True, nullable=False, default=datetime.utcnow)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # FK to one specific task (e.g., primary task)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=True)
    task = db.relationship('Tasks', foreign_keys=[task_id], backref='primary_project', lazy=True)

    # Tasks linked back to this project
    tasks = db.relationship('Tasks', foreign_keys='Tasks.project_id', backref='project', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'date_created': self.date_created.isoformat()
        }

class Tasks(db.Model, SerializerMixin):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    date_created = db.Column(db.DateTime, unique=False, nullable=True, default=datetime.utcnow)
    status = db.Column(db.String(255), default='pending', nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # This is the task → project association
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'date_created': self.date_created.isoformat(),
            'status': self.status
        }
