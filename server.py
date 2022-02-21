
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

    @staticmethod
    def add_group(name):
        newgroup = Group(name=name)
        db.session.add(newgroup)
        db.session.commit()
        return newgroup.id


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

    @staticmethod
    def add_test(name, group_id):
        newtest = Test(name=name, group_id=group_id)
        db.session.add(newtest)
        db.session.commit()
        return newtest.id


class Answers():
    @staticmethod
    def get_all():
        return db.session.query(Answer).all()

    @staticmethod
    def get_by_test(test_id):
        return db.session.query(Answer).filter(Answer.test_id == test_id)

    @staticmethod
    def add_answer(participant_id, test_id, question, answer):
        new_answer = Answer(participant_id, test_id, question, answer)
        db.session.add(new_answer)
        db.session.commit()
        return new_answer.id

# * -------------------------------
# * Main response handlers
# * -------------------------------

# ! Must-do tasks for 22.02

# TODO(): Put all functions in simple order, split static ones from others
# TODO(): Create all html files, check for all functions exists before run.
# TODO(): Create module for analytics
# TODO(): Take a look on javascript graph libraries working without npm
# TODO(): Or either find a way to bind Flask and Node.js modules together.
# ! Do not forget to bind css files!


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
    return render_template('group_by_id.html', group_info=Groups.get_group(group_id), tests=Tests.get_by_group(group_id))


@app.route('/tests/<test_id>')
def test_by_id(test_id):
    return render_template('test_by_id.html', test_info=Tests.get_test(test_id), group=Groups.get_group(Tests.get_test_group_id(test_id)))


@app.route('/test/<test_id>/add_form')
def test_add_answer(test_id):
    return render_template('test_add_form.html', participans=Participants.get_by_group(Tests.get_test_group_id(test_id)))


@app.route('/test/<test_id>/add_form/add', methods=['POST'])
def test_add_answer_request(test_id):
    req = json.loads(request.form.get('answers'))
    for answer in req['data']['answers']:
        newansw_id = Answers.add_answer(
            participant_id=req['data']['participant_id'], test_id=test_id, question=answer[0], answer=answer[1])
    return 200, 'OK'


@app.route('/groups/add_group')
def group_add():
    return render_template('group_add.html')


@app.route('/groups/add_group/add', methods=['POST'])
def group_add_request():
    group_id = Groups.add_group(name=request.form.get('name'))

    return redirect(url_for(f'/groups/{group_id}'))


@app.route('/groups/<group_id>/add_participant')
def group_add_participant():
    return render_template('group_add_participant.html')


@app.route('/groups/<group_id>/add_participant/add', methods=['POST'])
def group_add_participant_request(group_id):
    new_participant = Participants.add_participant(group_id=group_id, first_name=request.form.get(
        'first_name'), last_name=request.form.get('last_name'), middle_name=request.form.get('middle_name'))
    return render_template('group_add_participant_success.html')


@app.route('/tests/add_test')
def test_add():
    return render_template('test_add.html', groups=Groups.get_all())


@app.route('/tests/add_test/add', methods=['POST'])
def test_add_request():
    new_test = Tests.add_test(name=request.form.get(
        'test'), group_id=request.form.get('group_id'))
    return redirect(url_for(f'/tests/{test_id}'))


if __name__ == '__main__':
    app.run(port=PORT)
