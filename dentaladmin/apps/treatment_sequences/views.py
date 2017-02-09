# from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.contrib.messages import error, success

from apps.auth.models import Session
from apps.users.models import User
from apps.patients.models import Patient
from .models import Sequence
from dentaladmin.utils import validate_form

Sessions = Session()
Users = User()
Patients = Patient()
Sequences = Sequence()


def index(request, search=None):
    auth_user = Sessions.validate_auth(request)
    if auth_user is None:
        error(request, "You must log in first")
        return redirect('login')
    if 'search' in request.GET:
        search = request.GET['search']
    if auth_user['role'] == 'doctor':
        sequences = Sequences.find_sequences(search, auth_user['username'])
    else:
        sequences = Sequences.find_sequences(search)
    if sequences is None:
        return render(request, 'sequences/list.html', {'auth_user': auth_user, 'sequences': sequences})
    paginator = Paginator(sequences, 5)
    page = request.GET.get('page')
    try:
        pages = paginator.page(page)
    except PageNotAnInteger:
        pages = paginator.page(1)
    except EmptyPage:
        pages = paginator.page(paginator.num_pages)
    return render(request, 'sequences/list.html', {'auth_user': auth_user, 'sequences': sequences, 'pages': pages})


def create_sequence(request):
    auth_user = Sessions.validate_auth(request)
    if auth_user is None:
        error(request, "You must log in first")
        return redirect('login')
    doctors = Users.list_users('doctor')  # Combo data
    patients = Patients.list_patients()  # Combo data
    if request.method == 'GET':
        return render(request, 'sequences/create.html',
                      {'auth_user': auth_user, 'doctors': doctors, 'patients': patients})
    else:
        date = request.POST['date']
        shift = request.POST['shift']
        doctor_username = request.POST['doctor_username']
        patient_dni = request.POST['patient_dni']
        form = validate_form(request.POST)
        # From check patient
        if 'direct_appointment' in request.POST:
            code = Sequences.add_sequence_from_patient(date, shift, doctor_username, patient_dni)
            if code is False:
                error(request, "There was a problem creating the direct treatment sequence")
                return redirect('check_patient', dni=patient_dni)
            success(request, "Treatment sequence created successfully")
            return redirect('process_sequence', code=code)
        if form is not True:
            error(request, "There is a problem with your info, please check")
            return render(request, 'sequences/create.html',
                          {'auth_user': auth_user, 'doctors': doctors, 'patients': patients, 'date': date,
                           'shift': shift, 'doctor_username': doctor_username, 'patient_dni': patient_dni})
        result = Sequences.add_sequence(date, shift, doctor_username, patient_dni)
        if result is not True:
            error(request, result)
            return render(request, 'sequences/create.html',
                          {'auth_user': auth_user, 'doctors': doctors, 'patients': patients, 'date': date,
                           'shift': shift, 'doctor_username': doctor_username, 'patient_dni': patient_dni})
        success(request, "Treatment sequence registered successfully")
        response = redirect('sequences')
        return response


def process_sequence(request, code):
    auth_user = Sessions.validate_auth(request)
    if auth_user is None:
        error(request, "You must log in first")
        return redirect('login')
    if request.method == 'GET':
        sequence = Sequences.find_sequence(code)
        patient = Patients.find_patient(sequence['patient'])  # Combo data
        if sequence is None:
            error(request, "This sequence does not exist")
            return redirect('sequences')
        return render(request, 'sequences/process.html',
                      {'auth_user': auth_user, 'sequence': sequence, 'patient': patient})
    else:
        name = request.POST['name']
        date_of_birth = request.POST['date_of_birth']
        email = request.POST['email']
        phone = request.POST['phone']
        address = request.POST['address']
        visit_reason = request.POST['visit_reason']
        form = validate_form(request.POST)
        if form is not True:
            error(request, "There is a problem with your info, please check")
            return redirect('process_sequence', code=code)
        result = Sequences.process_sequence(code, name, date_of_birth, email, phone, address, visit_reason)
        if result is not True:
            error(request, result)
        else:
            success(request, "Treatment sequence updated successfully")
        return redirect('process_sequence', code=code)


def close_sequence(request, code):
    if Sessions.validate_auth(request) is None:
        error(request, "You must log in first")
        return redirect('login')
    result = Sequences.close_sequence(code)
    response = redirect('sequences')
    if result is not True:
        error(request, result)
        return response
    success(request, "Treatment sequence closed successfully")
    return response


def cancel_sequence(request, code):
    if Sessions.validate_auth(request) is None:
        error(request, "You must log in first")
        return redirect('login')
    result = Sequences.cancel_sequence(code)
    response = redirect('sequences')
    if result is not True:
        error(request, result)
        return response
    success(request, "Treatment sequence canceled successfully")
    return response


def invoice_sequence(request, code):
    if Sessions.validate_auth(request) is None:
        error(request, "You must log in first")
        return redirect('login')
    result = Sequences.invoice_sequence(code)
    response = redirect('sequences')
    if result is not True:
        error(request, result)
        return response
    success(request, "Treatment sequence deleted successfully")
    return response
