from dentaladmin import utils


database = utils.database_connection
errors = utils.database_errors


class Auth:

    def __init__(self):
        self.db = database
        self.users = self.db.users

    def login(self, username, password):
        query = {'username': username}
        user = self.users.find_one(query)
        if not user:
            return None
        if user['password'] != utils.make_pw_hash(password):
            return None
        return user


class Session:

    def __init__(self):
        self.db = database
        self.sessions = self.db.sessions

    def start_session(self, username, role):
        session_id = utils.get_random_str(32)
        session = {'username': username, 'role': role, '_id': session_id}
        try:
            self.sessions.insert_one(session)
        except errors.OperationFailure:
            return "oops, mongo error"
        return str(session['_id'])

    def end_session(self, session_id):
        if session_id is None:
            return "No session id found"
        try:
            self.sessions.delete_one({'_id': session_id})
        except errors.OperationFailure:
            return "oops, mongo error"
        return "Session ended"

    def get_session(self, session_id):
        if session_id is None:
            return
        session = self.sessions.find_one({'_id': session_id})
        if not session:
            return None
        return session

    def validate_auth(self, request):
        auth_user = None
        if 'session' in request.COOKIES:
            session_id = request.COOKIES['session']
            auth_user = self.get_session(session_id)
        return auth_user
