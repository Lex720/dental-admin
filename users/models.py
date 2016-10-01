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


class User:
    def __init__(self, db):
        self.db = db
        self.users = self.db.users

    def find_users(self, search):
        query = {}
        if search is not None:
            query = {'$or': [
                {'name': {'$regex': search, '$options': 'i'}},
                {'username': {'$regex': search, '$options': 'i'}},
                {'email': {'$regex': search, '$options': 'i'}},
                {'phone': {'$regex': search, '$options': 'i'}}
            ]}
        users = self.users.find(query)
        count = users.count()
        if count > 0:
            return users
        return None

    def find_user(self, username):
        user = self.users.find_one({'username': username})
        if not user:
            return None
        return user

    def add_user(self, name, email, phone, role, username, password):
        password_hash = make_pw_hash(password)
        user_exist = self.users.find_one({'username': username})
        email_exist = self.users.find_one({'email': email})
        if user_exist:
            return "Oops, username is already taken"
        if email_exist:
            return "Oops, email is already taken"
        user = {
            'name': name, 'email': email, 'phone': phone, 'role': role, 'username': username, 'password': password_hash
        }
        try:
            self.users.insert_one(user)
        except pymongo.errors.OperationFailure:
            return "oops, mongo error"
        return True

    def edit_user(self, username, name, email, phone, role):
        user = self.find_user(username)
        if user is None:
            return "User not found"
        try:
            self.users.update_one({'username': username},
                                  {'$set': {'name': name, 'email': email, 'phone': phone, 'role': role}})
        except pymongo.errors.OperationFailure:
            return "Oops, user not updated"
        return True

    def delete_user(self, username):
        query = {"username": username}
        user = self.find_user(username)
        if user is None:
            return "User not found"
        try:
            self.users.delete_one(query)
        except pymongo.errors.OperationFailure:
            return "Oops, user not deleted"
        return True
