from django.shortcuts import render


def index(request):
    """Muestra el inicio del modulo users"""
    return render(request, 'users/index.html')
