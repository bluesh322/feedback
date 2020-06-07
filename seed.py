"""Seed file for blogly"""

from models import User, Feedback, db
from app import app

# Create all tables
db.drop_all()
db.create_all()

# Add users

test = User.register("TestUser", "testpass")

test.email = "test@test.com"
test.first_name = "test"
test.last_name = "user"
test.is_admin = True

db.session.add(test)

db.session.commit()

test = User.register("OtherAdmin", "testpass")

test.email = "test3@test.com"
test.first_name = "other"
test.last_name = "admin"
test.is_admin = True

db.session.add(test)

db.session.commit()

test = Feedback(title="Test", content="BIG TEST LETS GOOO", username="TestUser")

db.session.add(test)

db.session.commit()

test = User.register("TestUser2", "testpass")

test.email = "test2@test.com"
test.first_name = "test"
test.last_name = "user"
test.is_admin = False

db.session.add(test)

db.session.commit()

test = Feedback(title="Test2", content="LET ME OUT", username="TestUser2")

db.session.add(test)

db.session.commit()