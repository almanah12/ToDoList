from todo import db, manager
from flask_login import UserMixin


class Task(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(15), default='Не выполнена')
    state_edit = db.Column(db.String(10), default='')

    def __repr__(self):
        return '<Task %r>' % self.username


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    password = db.Column(db.String(255), nullable=False)


@manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)