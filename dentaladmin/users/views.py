from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.contrib.messages import error, success
from auth.models import Session
from .models import User
from dentaladmin.utils import validate_form
from dentaladmin.utils import upload_file_verification, upload_file
# from django.http import HttpResponse


Sessions = Session()
Users = User()


def index(request, search=None):
    auth_user = Sessions.validate_auth(request)
    if auth_user is None:
        error(request, "You must log in first")
        return redirect('/login')
    if 'search' in request.GET:
        search = request.GET['search']
    users = Users.find_users(search)
    if users is None:
        return render(request, 'users/list.html', {'auth_user': auth_user, 'users': users})
    paginator = Paginator(users, 5)
    page = request.GET.get('page')
    try:
        pages = paginator.page(page)
    except PageNotAnInteger:
        pages = paginator.page(1)
    except EmptyPage:
        pages = paginator.page(paginator.num_pages)
    return render(request, 'users/list.html', {'auth_user': auth_user, 'users': users, 'pages': pages})


def create_user(request):
    auth_user = Sessions.validate_auth(request)
    if auth_user is None:
        error(request, "You must log in first")
        return redirect('/login')
    if request.method == 'GET':
        return render(request, 'users/create.html', {'auth_user': auth_user})
    else:
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        role = request.POST['role']
        username = request.POST['username']
        password = request.POST['password']
        pic = None
        if 'file' in request.FILES:
            pic = upload_file_verification(request.FILES['file'], username)
            if pic is False:
                error(request, "The image format must be jpg, png or bmp")
                return redirect(edit_user, username=username)
        form = validate_form(request.POST)
        if form is not True:
            error(request, "There is a problem with your info, please check")
            return render(request, 'users/create.html',
                          {'auth_user': auth_user, 'name': name, 'email': email, 'phone': phone, 'role': role,
                           'username': username})
        result = Users.add_user(name, email, phone, role, username, password, pic)
        if result is not True:
            error(request, result)
            return render(request, 'users/create.html',
                          {'auth_user': auth_user, 'name': name, 'email': email, 'phone': phone, 'role': role,
                           'username': username})
        if pic is not None:
            upload_file(pic, request.FILES['file'])
        success(request, "User registered successfully")
        response = redirect('/users')
        return response


def edit_user(request, username):
    auth_user = Sessions.validate_auth(request)
    if auth_user is None:
        error(request, "You must log in first")
        return redirect('/login')
    if request.method == 'GET':
        user = Users.find_user(username)
        if user is None:
            error(request, "This user does not exist")
            return redirect('/users')
        return render(request, 'users/edit.html', {'auth_user': auth_user, 'user': user})
    else:
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        role = request.POST['role']
        pic = None
        if 'file' in request.FILES:
            pic = upload_file_verification(request.FILES['file'], username)
            if pic is False:
                error(request, "The image format must be jpg, png or bmp")
                return redirect(edit_user, username=username)
        form = validate_form(request.POST)
        if form is not True:
            error(request, "There is a problem with your info, please check")
            return redirect(edit_user, username=username)
        result = Users.edit_user(username, name, email, phone, role, pic)
        if result is not True:
            error(request, result)
            return redirect(edit_user, username=username)
        if pic is not None:
            upload_file(pic, request.FILES['file'])
        response = redirect('/users')
        success(request, "User updated successfully")
        return response


def delete_user(request, username):
    if Sessions.validate_auth(request) is None:
        error(request, "You must log in first")
        return redirect('/login')
    result = Users.delete_user(username)
    response = redirect('/users')
    if result is not True:
        error(request, result)
        return response
    success(request, "User deleted successfully")
    return response
