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

    def find_users(self):
        users = self.users.find()
        count = users.count()
        if count > 0:
            return users
        return "There is no users"

    def find_user(self, username, email=None):
        if email is None:
            query = {"username": username}
        else:
            query = {"username": username, "email": email}
        user = self.users.find_one(query)
        if not user:
            return "User not found"
        return user

    def add_user(self, username, password, email):
        password_hash = make_pw_hash(password)
        user_exist = self.users.find_one({"username": username})
        email_exist = self.users.find_one({"email": email})
        if user_exist:
            return "oops, username is already taken"
        if email_exist:
            return "oops, email is already taken"
        user = {'username': username, 'password': password_hash, 'email': email}
        try:
            self.users.insert_one(user)
        except pymongo.errors.OperationFailure:
            return "oops, mongo error"
        return "user created"

    def login(self, username, password):
        query = {'username': username}
        user = self.users.find_one(query)
        if not user:
            return "User not in database"
        if user['password'] != make_pw_hash(password):
            return "User password is not a match"
        return user


class Session:

    def __init__(self, db):
        self.db = db
        self.sessions = db.sessions

    def start_session(self, username):
        session_id = get_random_str(32)
        session = {'username': username, '_id': session_id}
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
        return session

    def get_username(self, session_id):
        session = self.get_session(session_id)
        if not session:
            return "No session id found"
        else:
            return session["username"]
