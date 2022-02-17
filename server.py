from shlex import join
from flask import Flask, url_for, redirect, request
from sqlalchemy import null
import json
import os
from flask_sqlalchemy import SQLAlchemy

# * ----------------------------------------------------------------
# * Application creation and configuration
# * ----------------------------------------------------------------

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(os.path.dirname(__file__), 'data.socialdb')

db = SQLAlchemy(app)

# * -------------------------------
# * Definition of all models
# * -------------------------------


class Participant(db.Model):
    __tablename__ = 'participants'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_id = db.Column(db.Integer, nullable=False)
    first_name = db.Column(db.String(128), nullable=False)
    last_name = db.Column(db.String(128), nullable=False)
    middle_name = db.Column(db.String(128))


class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), nullable=False)


class Test(db.Model):
    __tablename__ = 'tests'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), nullable=False)
    group_id = db.Column(db.Integer, nullable=False)


class Answer(db.Model):
    __tablename__ = 'answers'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    participant_id = db.Column(db.Integer, nullable=False)
    test_id = db.Column(db.Integer, nullable=False)
    question = db.Column(db.Integer, nullable=False)
    answer = db.Column(db.Integer, nullable=False)

# * ----------------------------------------------------------------
# * Classes to work with the database
# * ----------------------------------------------------------------


class Participants():
    @staticmethod
    def get_all():
        return db.session.query(Participant).all()

    @staticmethod
    def get_by_group(group_id):
        return db.session.query(Participant).filter(Group.id == group_id)

    @staticmethod
    def get_participant(participant_id):
        return db.session.query(Participant).filter(Participant.id == participant_id)

    @staticmethod
    def add_participant(group, first, last, middle=''):
        new_participant = Participant(
            group_id=group, first_name=first, last_name=last, middle_name=middle)
        db.session.add(new_participant)
        db.session.commit()
        return 


class Groups():
    @staticmethod
    def get_all():
        return db.session.query(Group).all()

    @staticmethod
    def get_group(group_id):
        return db.session.query(Group).filter(Group.id == group_id)


class Tests():
    @staticmethod
    def get_all():
        return db.session.query(Test).all()

    @staticmethod
    def get_by_group(group_id):
        return db.session.query(Test).filter(Test.group_id == group_id)

    @staticmethod
    def get_test(test_id):
        return db.session.query(Test).filter(Test.id == test_id)


class Answer():
    @staticmethod
    def get_all():
        return db.session.query(Answer).all()

    @staticmethod
    def get_by_test(test_id):
        return db.session.query(Answer).filter(Answer.test_id == test_id)

# * -------------------------------
# * Main response handlers
# * -------------------------------


@app.route('/', methods=['GET'])
def index():
    return app.send_static_file('app.html')


@app.route('/api/participants/get_all')
def participants_get_all():
    try:
        resp = {
            'status': 'success',
            'result': {
                'participants': Participants.get_all()
            }
        }

    except:
        resp = {
            'status': 'error',
            'error_code': 500,
        }
    return json.dumps(resp)


@app.route('/api/participants/get/<participant_id>')
def participant_get(participant_id):
    try:
        resp = {
            'status': 'success',
            'result': {
                'participant': Participants.get_participant(int(participant_id))
            }
        }
    except:
        resp = {
            'status': 'error',
            'error_code': 500,
        }

    return json.dumps(resp)


@app.route('/api/participants/get_by_group/<group_id>')
def participant_get_by_group(group_id):
    try:
        resp = {
            'status': 'success',
            'result': {
                'participant': Participants.get_by_group(int(group_id))
            }
        }

    except:
        resp = {
            'status': 'error',
            'error_code': 500,
        }

    return json.dumps(resp)

@app.route('/api/participants/add', methods=['POST'])
def participant_add():
    participant_data = json.loads(request.form.get('new_participant'))
    new_participant_id = Participants.add(group=participant_data['data']['group'], first=participant_data['data']['first'], last=participant_data['data']['last'], middle=participant_data['data']['middle'])
    
    resp = {
        'status': 'success',
        'result': {
            'new_participant_id': new_participant_id
        }
    }
    return json.dumps(resp)


if __name__ == '__main__':
    app.run(port=8443)
