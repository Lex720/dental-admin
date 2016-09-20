from django.shortcuts import render


def dashboard(request):
    """Método que muestra el dashboard"""
    return render(request, 'auth/dashboard.html')
