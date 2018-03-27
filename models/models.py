from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import datetime

db = SQLAlchemy()


class AnalysisResults(db.Model):
    __tablename__ = 'result'
    id = db.Column(db.Integer, primary_key=True)
    pos = db.Column(db.Float, nullable=False)
    neg = db.Column(db.Float, nullable=False)
    medicine = db.Column(db.Float, nullable=False)
    politics = db.Column(db.Float, nullable=False)
    program = db.Column(db.Float, nullable=False)
    reddit_comment = db.relationship("RedditComments", uselist=False, back_populates="result")
    twitter_comment = db.relationship("TwitterComments", uselist=False, back_populates="result")

    def __repr__(self):
        return str(self.id)


class RedditComments(db.Model):
    __tablename__ = 'reddit'
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(100), index=True, nullable=False)
    timestamp = db.Column(db.Float, index=True, nullable=False)
    result_id = db.Column(db.Integer, db.ForeignKey('result.id'))
    result = db.relationship("AnalysisResults", back_populates="reddit_comment")

    def __repr__(self):
        return "%s - %s" % (self.id, self.user)


class TwitterComments(db.Model):
    __tablename__ = 'twitter'
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(100), index=True, nullable=False)
    timestamp = db.Column(db.Float, index=True, nullable=False)
    result_id = db.Column(db.Integer, db.ForeignKey('result.id'))
    result = db.relationship("AnalysisResults", back_populates="twitter_comment")

    def __repr__(self):
        return "%s - %s" % (self.id, self.user)


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    social_id = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False)
    nickname = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)

    def __init__(self, social_id, email, nickname, password,
                 confirmed, admin=False, confirmed_on=None):
        from server import bcrypt
        self.social_id = social_id
        self.email = email
        self.nickname = nickname
        self.password = bcrypt.generate_password_hash(password)
        self.registered_on = datetime.datetime.now()
        self.admin = admin
        self.confirmed = confirmed
        self.confirmed_on = confirmed_on

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<email {}'.format(self.email)
