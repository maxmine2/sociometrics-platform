
# * Comments in this file will be much easier to read
# * If you have "Better Comments" extension downloaded
# * and enabled in your VS Code settings (or any other IDE)

from flask import Flask, url_for, redirect, request, render_template
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

HOST = 'localhost'
PORT = 8443


DOMAIN = f'{HOST}:{PORT}'

db = SQLAlchemy(app)

# * ------------------------------------------
# * Definition of all database models
# * ------------------------------------------


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
# * Classes to wrap over dry SQLAlchemy interface
# * ----------------------------------------------------------------


class Participants():
    @staticmethod
    def get_all():
        data = db.session.query(Participant).all()
        return [[participant.id, participant.first_name, participant.middle_name, participant.last_name, participant.group_id] for participant in data]

    @staticmethod
    def get_by_group(group_id):
        data = db.session.query(Participant).filter(Group.id == group_id)
        return [[participant.id, participant.first_name, participant.middle_name, participant.last_name, participant.group_id] for participant in data]


    @staticmethod
    def get_participant(participant_id):
        data = db.session.query(Participant).filter(Participant.id == participant_id)
        return [[participant.id, participant.first_name, participant.middle_name, participant.last_name, participant.group_id] for participant in data]

    @staticmethod
    def add_participant(group, first, last, middle=''):
        new_participant = Participant(
            group_id=group, first_name=first, last_name=last, middle_name=middle)
        db.session.add(new_participant)
        db.session.commit()
        return new_participant.id


class Groups():
    @staticmethod
    def get_all():
        data = db.session.query(Group).all()
        return [[group.id, group.name] for group in data]

    @staticmethod
    def get_group(group_id):
        data = db.session.query(Group).filter(Group.id == group_id)
        return [[group.id, group.name] for group in data]

    @staticmethod
    def add_group(name):
        newgroup = Group(name=name)
        db.session.add(newgroup)
        db.session.commit()
        return newgroup.id


class Tests():
    @staticmethod
    def get_all():
        data = db.session.query(Test).all()
        return [[test.id, test.name, test.group_id] for test in data]

    @staticmethod
    def get_by_group(group_id):
        data = db.session.query(Test).filter(Test.group_id == group_id)
        return [[test.id, test.name, test.group_id] for test in data]

    @staticmethod
    def get_test(test_id):
        data = db.session.query(Test).filter(Test.id == test_id)
        return [[test.id, test.name, test.group_id] for test in data]

    @staticmethod
    def get_test_group_id(test_id):
        return db.session.query(Test).filter(Test.id == test_id)[0].group_id

        

    @staticmethod
    def add_test(name, group_id):
        newtest = Test(name=name, group_id=group_id)
        db.session.add(newtest)
        db.session.commit()
        return newtest.id


class Answers():
    @staticmethod
    def get_all():
        data = db.session.query(Answer).all()
        return [[answer.id, answer.participant_id, answer.group_id, answer.question, answer.answer] for answer in data]

    @staticmethod
    def get_by_test(test_id):
        data = db.session.query(Answer).filter(Answer.test_id == test_id)
        return [[answer.id, answer.participant_id, answer.group_id, answer.question, answer.answer] for answer in data]

    @staticmethod
    def add_answer(participant_id, test_id, question, answer):
        new_answer = Answer(participant_id, test_id, question, answer)
        db.session.add(new_answer)
        db.session.commit()
        return new_answer.id

# * -------------------------------
# * Main response handlers
# * -------------------------------

# * -----------------------------------
# * Static functions
# * -----------------------------------


@app.route('/', methods=['GET'])
def index():
    return app.send_static_file('app.html')


@app.route('/groups')
def groups():
    return render_template('groups.html', groups=Groups.get_all())


@app.route('/tests')
def tests():
    return render_template('tests.html', tests=Tests.get_all())


@app.route('/groups/<group_id>')
def group_by_id(group_id):
    return render_template('group_by_id.html', group=Groups.get_group(group_id)[0], participants=Participants.get_by_group(group_id), len_participants=len(Participants.get_by_group(group_id)))


@app.route('/groups/add_group')
def group_add():
    return render_template('group_add.html')


@app.route('/groups/<group_id>/add_participant')
def group_add_participant(group_id):
    return render_template('group_add_participant.html', group_id=group_id)


@app.route('/tests/<test_id>')
def test_by_id(test_id):
    return render_template('test_by_id.html', test=Tests.get_test(test_id)[0])


@app.route('/tests/<test_id>/add_form')
def test_add_answer(test_id):
    return render_template('test_add_form.html', persons=Participants.get_by_group(Tests.get_test_group_id(test_id)), test_id=test_id)


@app.route('/tests/add_test')
def test_add():
    return render_template('test_add.html', groups=Groups.get_all())


# * --------------------------------------
# * Non-static functions
# * --------------------------------------

@app.route('/groups/add_group/add', methods=['POST'])
def group_add_request():
    group_id = Groups.add_group(name=request.form.get('name'))

    return redirect(url_for(f'groups'))


@app.route('/groups/<group_id>/add_participant/add', methods=['POST'])
def group_add_participant_request(group_id):
    new_participant = Participants.add_participant(group=group_id, first=request.form.get(
        'first_name'), last=request.form.get('last_name'), middle=request.form.get('middle_name'))
    return render_template('group_add_participant_success.html', group_id=group_id)


@app.route('/tests/add_test/add', methods=['POST'])
def test_add_request():
    new_test = Tests.add_test(name=request.form.get(
        'test'), group_id=request.form.get('group_id'))
    return redirect(url_for(f'tests'))


@app.route('/test/<test_id>/add_form/add', methods=['POST'])
def test_add_answer_request(test_id):
    req = json.loads(request.form.get('answers'))
    for answer in req['data']['answers']:
        newansw_id = Answers.add_answer(
            participant_id=req['data']['participant_id'], test_id=test_id, question=answer[0], answer=answer[1])
    return 200, 'OK'


if __name__ == '__main__':
    app.run(port=PORT)
