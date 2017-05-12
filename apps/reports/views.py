# from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.contrib.messages import error

from apps.auth.models import Session
from apps.treatment_sequences.models import Sequence

Sessions = Session()
Sequences = Sequence()


def total(request, search=None):
    auth_user = Sessions.validate_auth(request)
    if auth_user is None:
        error(request, "You must log in first")
        return redirect('login')
    if auth_user['role'] == 'doctor':
        error(request, "You don't have permissions for this report")
        return redirect('/')
    if 'search' in request.GET:
        search = request.GET['search']
    reports = Sequences.report_sequences(search)
    total_amount = Sequences.report_sequences_total(search)
    # total_amount = sum(d['total'] for d in reports)
    if reports is None:
        return render(request, 'reports/total.html', {'auth_user': auth_user, 'reports': reports})
    paginator = Paginator(reports, 5)
    page = request.GET.get('page')
    try:
        pages = paginator.page(page)
    except PageNotAnInteger:
        pages = paginator.page(1)
    except EmptyPage:
        pages = paginator.page(paginator.num_pages)
    return render(request, 'reports/total.html',
                  {'auth_user': auth_user, 'reports': reports, 'total_amount': total_amount, 'pages': pages})


def payment(request, search=None):
    auth_user = Sessions.validate_auth(request)
    if auth_user is None:
        error(request, "You must log in first")
        return redirect('login')
    if 'search' in request.GET:
        search = request.GET['search']
    reports = Sequences.report_sequences(search, auth_user['username'])
    total_sequence = Sequences.report_sequences_total(search, auth_user['username'])
    total_amount = round((total_sequence * 40) / 100, 2)
    # total_amount = sum(d['total'] for d in reports)
    if reports is None:
        return render(request, 'reports/payment.html', {'auth_user': auth_user, 'reports': reports})
    paginator = Paginator(reports, 5)
    page = request.GET.get('page')
    try:
        pages = paginator.page(page)
    except PageNotAnInteger:
        pages = paginator.page(1)
    except EmptyPage:
        pages = paginator.page(paginator.num_pages)
    return render(request, 'reports/payment.html',
                  {'auth_user': auth_user, 'reports': reports, 'total_amount': total_amount, 'pages': pages})
