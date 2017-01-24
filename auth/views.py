from django.shortcuts import render, redirect
from django.contrib.messages import error, success
from pymongo import MongoClient
from auth.models import Auth, Session
from users.models import User

client = MongoClient('db', 27017)
db = client.wolfadmin
Sessions = Session(db)
Auths = Auth(db)
Users = User(db)


def validate_auth(request):
    auth_user = None
    if 'session' in request.COOKIES:
        session_id = request.COOKIES['session']
        auth_user = Sessions.get_session(session_id)
    return auth_user


def validate_form(request):
    for key in request.POST:
        value = request.POST[key]
        if value is None or value == "":
            return False
    if 'password' in request.POST:
        if request.POST['password'] != request.POST['password2']:
            return False
    return True


def signup(request):
    if request.method == 'GET':
        return render(request, 'auth/signup.html')
    else:
        name = request.POST['name']  # "Alexander Gonzalez"
        email = request.POST['email']  # "alexjgonzalezm@gmail.com"
        phone = request.POST['phone']  # "04128418822"
        role = request.POST['role']  # "admin"
        username = request.POST['username']  # "alex"
        password = request.POST['password']  # "123456"
        form = validate_form(request)
        if form is not True:
            error(request, "There is a problem with your info, please check")
            return render(request, 'auth/signup.html',
                          {'name': name, 'email': email, 'phone': phone, 'role': role,
                           'username': username})
        result = Users.add_user(name, email, phone, role, username, password)
        if result is not True:
            error(request, result)
            return render(request, 'auth/signup.html',
                          {'name': name, 'email': email, 'phone': phone, 'role': role,
                           'username': username})
        success(request, "Registered successfully")
        response = redirect('/login')
        return response


def login(request):
    if request.method == 'GET':
        return render(request, 'auth/login.html')
    else:
        if validate_auth(request) is not None:
            error(request, "You are already logged in")
            return redirect('/')
        username = request.POST['username']
        password = request.POST['password']
        user = Auths.login(username, password)
        if user is None:
            error(request, "User authentication error")
            return redirect('/login')
        session_id = Sessions.start_session(user["username"], user["role"])
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
