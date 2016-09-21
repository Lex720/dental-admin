from django.shortcuts import render


def dashboard(request):
    """Método que muestra el dashboard"""
    return render(request, 'auth/dashboard.html')


def login(request):
    """Método que muestra el login"""
    return render(request, 'auth/login.html')


def signup(request):
    """Método que muestra el signup"""
    return render(request, 'auth/signup.html')
