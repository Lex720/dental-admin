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


def validate_form(request):
    for key in request.POST:
        value = request.POST[key]
        if value is None or value == '':
            return False
    if request.POST["password"] != request.POST["password2"]:
        return False
    return True


def index(request, name=None):
    username = validate_auth(request)
    if username is None:
        error(request, "You must log in first")
        return redirect('/login')
    if 'name' in request.GET:
        name = request.GET['name']
    users = user.find_users(name)
    return render(request, 'users/list.html', {'users': users})


def create_user(request):
    if request.method == 'GET':
        username = validate_auth(request)
        if username is None:
            error(request, "You must log in first")
            return redirect('/login')
        return render(request, 'users/create.html')
    else:
        form = validate_form(request)
        if form is not True:
            error(request, "There is a problem with your info, please check")
            return redirect('/users/create')

        name = request.POST['name']  # "Alexander Gonzalez"
        email = request.POST['email']  # "alexjgonzalezm@gmail.com"
        phone = request.POST['phone']  # "04128418822"
        role = request.POST['role']  # "admin"
        username = request.POST['username']  # "alex"
        password = request.POST['password']  # "123456"

        result = user.add_user(name, email, phone, role, username, password)
        if result is not True:
            error(request, result)
            return redirect('/users/create')

        response = redirect('/users')
        success(request, "User registered successfully")
        return response


def delete_user(request, username):
    result = user.delete_user(username)
    if result is not True:
        error(request, result)
        return redirect('/users')
    response = redirect('/users')
    success(request, "User deleted successfully")
    return response
