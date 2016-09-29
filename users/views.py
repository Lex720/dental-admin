from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.messages import error, success
from pymongo import MongoClient
from auth.models import Session
from users.models import User

client = MongoClient('db', 27017)
db = client.wolfadmin
session = Session(db)
user = User(db)


def validate_auth(request):
    username = None
    if "session" in request.COOKIES:
        session_id = request.COOKIES['session']
        username = session.get_username(session_id)
    return username


def validate_form(request, fields):
    for key in fields:
        value = fields[key]
        if value is None or value == '':
            return False
    if fields["password"] != fields["password2"]:
        return False
    return True


def index(request):
    username = validate_auth(request)
    if username is None:
        error(request, "You must log in first")
        return redirect('/login')
    users = user.find_users()
    return render(request, 'users/list.html', {'users': users})


def create_user(request):
    if request.method == 'GET':
        username = validate_auth(request)
        if username is None:
            error(request, "You must log in first")
            return redirect('/login')
        return render(request, 'users/create.html')
    else:
        name = request.POST['name']  # "Alexander Gonzalez"
        email = request.POST['email']  # "alexjgonzalezm@gmail.com"
        phone = request.POST['phone']  # "04128418822"
        role = request.POST['role']  # "admin"
        username = request.POST['username']  # "alex"
        password = request.POST['password']  # "123456"
        # password2 = request.POST['password2'] # "123456"

        form = validate_form(request, request.POST)
        if form is not True:
            error(request, "There is a problem with your info, please check")
            return redirect('/users/create')

        result = user.add_user(name, email, phone, role, username, password)
        if result is not True:
            error(request, result)
            return redirect('/users/create')

        response = redirect('/users')
        success(request, "User registered successfully")
        return response


def find_user(request):
    user1 = user.find_user("alex")
    return HttpResponse(user1)
