from django.shortcuts import render
from django.http import HttpResponse
from pymongo import MongoClient
from users.models import User

client = MongoClient('db', 27017)
db = client.wolfadmin
user = User(db)


def index(request):
    """Muestra el inicio del modulo users"""
    return render(request, 'users/index.html')


def find_users(request):
    users = user.find_users()
    return HttpResponse(users)


def find_user(request):
    user1 = user.find_user("alex")
    return HttpResponse(user1)


def add_user(request):
    username = "alex"
    password = "1234"
    email = "alexjgonzalezm@gmail.com"
    message = user.add_user(username, password, email)
    return HttpResponse(message)
