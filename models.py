from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime
from sqlalchemy.orm import backref

db = SQLAlchemy()

bcrypt = Bcrypt()


def connect_db(app):
    """Connect to the database"""
    db.app = app
    db.init_app(app)


class User(db.Model):
    """Users"""

    __tablename__ = "users"

    def __repr__(self):
        """Show info about a user"""
        u = self
        return f"<User {u.username} {u.password}>"

    def serialize(self):
        return {
            'username': self.username
        }

    username = db.Column(db.Unicode(20), primary_key=True,
                         nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.Unicode(50), nullable=False, unique=True)
    first_name = db.Column(db.Unicode(30), nullable=False)
    last_name = db.Column(db.Unicode(30), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    feedbacks = db.relationship('Feedback', cascade="all,delete", backref="user_id")



    @classmethod
    def register(cls, username, pwd):
        """Register user w/hashed password & return user."""

        hashed = bcrypt.generate_password_hash(pwd)
        # turn bytestring into unicode utf8 string
        hashed_utf8 = hashed.decode("utf8")

        return cls(username=username, password=hashed_utf8)

    @classmethod
    def authenticate(cls, username, pwd):
        """Validate user exists & password is correct,
        return user if valid; else return False"""

        u = User.query.filter_by(username=username).first()

        if u and bcrypt.check_password_hash(u.password, pwd):
            # return user instance
            return u
        else:
            return False


class Feedback(db.Model):
    """Feedbacks"""

    __tablename__ = "feedbacks"

    def __repr__(self):
        """Show info about a user"""
        f = self
        return f"<Feedback {f.title} {f.content}>"

    def serialize(self):
        return {
            'title': self.title
        }

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.Unicode(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    username = db.Column(db.Unicode(20), db.ForeignKey('users.username'))
    
