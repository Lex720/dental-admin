from django.shortcuts import render, redirect
from django.http import HttpResponse
from pymongo import MongoClient
from auth.models import Auth, Session

client = MongoClient('db', 27017)
db = client.wolfadmin
auth = Auth(db)
session = Session(db)


def login(request):
    if request.method == "GET":
        return render(request, 'auth/login.html')
    else:
        username = request.POST['username']
        password = request.POST['password']
        user = auth.login(username, password)
        session_id = session.start_session(user["username"])
        response = redirect("/")
        response.set_cookie(key="session", value=session_id)
        return response


def logout(request):
    response = redirect("/login")
    if "session" in request.COOKIES:
        session_id = request.COOKIES["session"]
        session.end_session(session_id)
        response.delete_cookie("session")
    return response


def dashboard(request):
    username = None
    if "session" in request.COOKIES:
        session_id = request.COOKIES["session"]
        username = session.get_username(session_id)  # see if user is logged in
    if username is None:
        return redirect('/login')
    return render(request, 'auth/dashboard.html', {'username': username})


def test(request):
    # db.sessions.delete_many({})
    sessions = db.sessions.find()
    if "session" in request.COOKIES:
        session = request.COOKIES["session"]
    else:
        session = "no hay session"
    return HttpResponse(session)


def signup(request):
    """Método que muestra el signup"""
    return render(request, 'auth/signup.html')


def find_users(request):
    users = auth.find_users()
    return HttpResponse(users)


def find_user(request):
    user = auth.find_user("alex")
    return HttpResponse(user)


def add_user(request):
    username = "alex"
    password = "1234"
    email = "alexjgonzalezm@gmail.com"
    message = auth.add_user(username, password, email)
    return HttpResponse(message)
