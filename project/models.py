from flask_login import UserMixin
from . import db


class SoundcloudToken(db.Model):
    __tablename__ = 'soundcloud_tkn'

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(1000), default='')

    def __repr__(self):
        return '<id {}>'.format(self.id)


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    spotify_tkn = db.Column(db.String(1000), default='')
    deezer_tkn = db.Column(db.String(1000), default='')

    def __init__(self, email, password, name):
        self.email = email
        self.password = password
        self.name = name

    def __repr__(self):
        return '<id {}>'.format(self.id)
