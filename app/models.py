import base64
import os
from datetime import datetime, timedelta
from time import time
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False)
    picture = db.Column(db.String(250))
    address = db.Column(db.String(250))
    password_hash = db.Column(db.String(128))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)
    issues = db.relationship('Issues', backref='author', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'picture': self.picture,
            'address': self.address,
            'last_seen': self.last_seen.isoformat() + 'Z',
            'issue_count': self.issues.count()
        }
        return data

    def from_dict(self, data, new_user=False):
        for field in ['name', 'email', 'picture', 'address']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])

    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return {'id': self.id, 'token': self.token}
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return {'id': self.id, 'token': self.token}

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Issues(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lat = db.Column(db.String(250), nullable=False)
    longi = db.Column(db.String(250), nullable=False)
    picture = db.Column(db.String(250), nullable=False)
    comment = db.Column(db.String(250), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    resolved = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_dict(self):
        if self.author:
            dict_user = self.author.to_dict()
        data = {
            'id': self.id,
            'lat': self.lat,
            'longi': self.longi,
            'picture': self.picture,
            'comment': self.comment,
            'user_id': self.user_id,
            'timestamp': self.timestamp,
            'resolved': self.resolved,
            'user': dict_user
        }
        return data

    def from_dict(self, data, new_issue=False):
        for field in ['lat', 'longi', 'picture', 'comment', 'user_id']:
            if field in data:
                setattr(self, field, data[field])
