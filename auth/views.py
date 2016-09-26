from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.messages import error, success
from pymongo import MongoClient
from auth.models import Auth, Session

client = MongoClient('db', 27017)
db = client.wolfadmin
auth = Auth(db)
session = Session(db)


def validate_auth(request):
    username = None
    if "session" in request.COOKIES:
        session_id = request.COOKIES['session']
        username = session.get_username(session_id)
    return username


def signup(request):
    """Método que muestra el signup"""
    return render(request, 'auth/signup.html')


def login(request):
    if request.method == 'GET':
        return render(request, 'auth/login.html')
    else:
        username = request.POST['username']
        password = request.POST['password']
        # value = "User: {0}, Pass: {1}".format(username, password)
        # return HttpResponse(value)
        user = auth.login(username, password)
        if user is None:
            error(request, "User authentication error")
            return redirect('/login')
        session_id = session.start_session(user["username"])
        response = redirect('/')
        response.set_cookie(key="session", value=session_id)
        success(request, "Logged in successfully")
        return response


def logout(request):
    response = redirect('/login')
    if "session" in request.COOKIES:
        session_id = request.COOKIES['session']
        session.end_session(session_id)
        response.delete_cookie('session')
    success(request, "Logged out successfully")
    return response


def dashboard(request):
    username = validate_auth(request)
    if username is None:
        error(request, "You must log in first")
        return redirect('/login')
    return render(request, 'auth/dashboard.html', {'username': username})


def test(request):
    # db.sessions.delete_many({})
    sessions = db.sessions.find()
    session = "No hay sesion"
    if "session" in request.COOKIES:
        session = request.COOKIES['session']
    else:
        session = "no hay session"
    response = "Sesiones en BD: {0} <br><br> Sesiones activas: {1}".format(sessions, session)
    return HttpResponse(response)
