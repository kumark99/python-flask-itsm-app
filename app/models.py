from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='User') # Admin, Agent, User

    # Relationships
    incidents_created = db.relationship('Incident', backref='author', lazy='dynamic', foreign_keys='Incident.user_id')
    incidents_assigned = db.relationship('Incident', backref='assignee', lazy='dynamic', foreign_keys='Incident.assigned_to_id')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Incident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    description = db.Column(db.Text)
    category = db.Column(db.String(50), default='General') # Hardware, Software, Network, Access, General
    status = db.Column(db.String(20), default='Open') # Open, In Progress, Resolved, Closed
    priority = db.Column(db.String(20), default='Medium') # Low, Medium, High, Critical
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'status': self.status,
            'priority': self.priority,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'created_by': self.author.username if self.author else None,
            'assigned_to': self.assignee.username if self.assignee else None
        }

    def __repr__(self):
        return f'<Incident {self.title}>'
