from django.shortcuts import render, redirect
from django.contrib.messages import error, success
from pymongo import MongoClient
from auth.models import Session
from users.models import User

client = MongoClient('db', 27017)
db = client.wolfadmin
Sessions = Session(db)
Users = User(db)


def validate_auth(request):
    auth_user = None
    if 'session' in request.COOKIES:
        session_id = request.COOKIES['session']
        auth_user = Sessions.get_username(session_id)
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


def index(request, search=None):
    auth_user = validate_auth(request)
    if auth_user is None:
        error(request, "You must log in first")
        return redirect('/login')
    if 'search' in request.GET:
        search = request.GET['search']
    users = Users.find_users(search)
    return render(request, 'users/list.html', {'users': users})


def create_user(request):
    if request.method == 'GET':
        auth_user = validate_auth(request)
        if auth_user is None:
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
        form = validate_form(request)
        if form is not True:
            error(request, "There is a problem with your info, please check")
            return render(request, 'users/create.html',
                          {'name': name, 'email': email, 'phone': phone, 'role': role, 'username': username})
        result = Users.add_user(name, email, phone, role, username, password)
        if result is not True:
            error(request, result)
            return render(request, 'users/create.html',
                          {'name': name, 'email': email, 'phone': phone, 'role': role, 'username': username})
        response = redirect('/users')
        success(request, "User registered successfully")
        return response


def edit_user(request, username):
    if request.method == 'GET':
        auth_user = validate_auth(request)
        if auth_user is None:
            error(request, "You must log in first")
            return redirect('/login')
        user = Users.find_user(username)
        if user is None:
            error(request, "This user does not exist")
            return redirect('/users')
        return render(request, 'users/edit.html', {'user': user})
    else:
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        role = request.POST['role']
        form = validate_form(request)
        if form is not True:
            error(request, "There is a problem with your info, please check")
            return redirect(edit_user, username=username)
        result = Users.edit_user(username, name, email, phone, role)
        if result is not True:
            error(request, result)
            return redirect(edit_user, username=username)
        response = redirect('/users')
        success(request, "User updated successfully")
        return response


def delete_user(request, username):
    auth_user = validate_auth(request)
    if auth_user is None:
        error(request, "You must log in first")
        return redirect('/login')
    result = Users.delete_user(username)
    response = redirect('/users')
    if result is not True:
        error(request, result)
        return response
    success(request, "User deleted successfully")
    return response
