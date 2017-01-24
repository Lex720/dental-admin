import hashlib
import random
import string
import pymongo


def make_pw_hash(password):
    password = password.encode('utf-8')
    return hashlib.sha256(password).hexdigest()


def get_random_str(num_chars):
    random_string = ""
    for i in range(num_chars):
        random_string = random_string + random.choice(string.ascii_letters)
    return random_string


class Auth:

    def __init__(self, db):
        self.db = db
        self.users = self.db.users

    def login(self, username, password):
        query = {'username': username}
        user = self.users.find_one(query)
        if not user:
            return None
        if user['password'] != make_pw_hash(password):
            return None
        return user


class Session:

    def __init__(self, db):
        self.db = db
        self.sessions = db.sessions

    def start_session(self, username, role):
        session_id = get_random_str(32)
        session = {'username': username, 'role': role, '_id': session_id}
        try:
            self.sessions.insert_one(session)
        except pymongo.errors.OperationFailure:
            return "oops, mongo error"
        return str(session['_id'])

    def end_session(self, session_id):
        if session_id is None:
            return "No session id found"
        try:
            self.sessions.delete_one({'_id': session_id})
        except pymongo.errors.OperationFailure:
            return "oops, mongo error"
        return "Session ended"

    def get_session(self, session_id):
        if session_id is None:
            return
        session = self.sessions.find_one({'_id': session_id})
        if not session:
            return None
        return session
