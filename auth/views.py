from django.shortcuts import render, redirect
from django.contrib.messages import error, success
from pymongo import MongoClient
from auth.models import Auth, Session

client = MongoClient('db', 27017)
db = client.wolfadmin
Sessions = Session(db)
Auths = Auth(db)


def validate_auth(request):
    auth_user = None
    if 'session' in request.COOKIES:
        session_id = request.COOKIES['session']
        auth_user = Sessions.get_username(session_id)
    return auth_user


def signup(request):
    """Método que muestra el signup"""
    return render(request, 'auth/signup.html')


def login(request):
    if request.method == 'GET':
        return render(request, 'auth/login.html')
    else:
        auth_user = validate_auth(request)
        if auth_user is not None:
            error(request, "You are already logged in")
            return redirect('/')
        username = request.POST['username']
        password = request.POST['password']
        user = Auths.login(username, password)
        if user is None:
            error(request, "User authentication error")
            return redirect('/login')
        session_id = Sessions.start_session(user["username"])
        response = redirect('/')
        response.set_cookie(key="session", value=session_id)
        success(request, "Logged in successfully")
        return response


def logout(request):
    response = redirect('/login')
    if "session" in request.COOKIES:
        session_id = request.COOKIES['session']
        Sessions.end_session(session_id)
        response.delete_cookie('session')
    success(request, "Logged out successfully")
    return response


def dashboard(request):
    auth_user = validate_auth(request)
    if auth_user is None:
        error(request, "You must log in first")
        return redirect('/login')
    return render(request, 'auth/dashboard.html', {'auth_user': auth_user})
