from dentaladmin import utils


database = utils.database_connection
errors = utils.database_errors


class User:

    def __init__(self):
        self.db = database
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

    def add_user(self, name, email, phone, role, username, password, pic=None):
        password_hash = utils.make_pw_hash(password)
        user_exist = self.users.find_one({'username': username})
        email_exist = self.users.find_one({'email': email})
        if user_exist:
            return "Oops, username is already taken"
        if email_exist:
            return "Oops, email is already taken"
        user = {
            'name': name, 'email': email, 'phone': phone, 'role': role, 'pic': pic, 'username': username,
            'password': password_hash
        }
        try:
            self.users.insert_one(user)
        except errors.OperationFailure:
            return "oops, mongo error"
        return True

    def edit_user(self, username, name, email, phone, role, pic=None):
        user = self.find_user(username)
        if user is None:
            return "User not found"
        try:
            if pic is None:
                pic = user['pic']
            self.users.update_one({'username': username},
                                  {'$set': {'name': name, 'email': email, 'phone': phone, 'role': role, 'pic': pic}})
        except errors.OperationFailure:
            return "Oops, user not updated"
        return True

    def delete_user(self, username):
        query = {"username": username}
        user = self.find_user(username)
        if user is None:
            return "User not found"
        try:
            self.users.delete_one(query)
        except errors.OperationFailure:
            return "Oops, user not deleted"
        return True
