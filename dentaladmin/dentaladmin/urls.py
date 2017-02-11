"""dentaladmin URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url

from apps.auth import views as auth_views
from apps.users import views as users_views
from apps.patients import views as patients_views
from apps.treatments import views as treatments_views
from apps.treatment_sequences import views as sequences_views

urlpatterns = [
    # Dashboard
    url(r'^$', auth_views.dashboard, name="dashboard"),
    # Login & Signup
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout'),
    url(r'^signup/$', auth_views.signup, name='signup'),
    # Users
    url(r'^users/$', users_views.index, name='users'),
    url(r'^users/create/$', users_views.create_user, name='create_user'),
    url(r'^users/edit/(?P<username>\w+)/$', users_views.edit_user, name='edit_user'),
    url(r'^users/delete/(?P<username>\w+)/$', users_views.delete_user, name='delete_user'),
    # Patients
    url(r'^patients/$', patients_views.index, name='patients'),
    url(r'^patients/create/$', patients_views.create_patient, name='create_patient'),
    url(r'^patients/edit/(?P<dni>\d+)/$', patients_views.edit_patient, name='edit_patient'),
    url(r'^patients/check/(?P<dni>\d+)/$', patients_views.check_patient, name='check_patient'),
    url(r'^patients/check/(?P<dni>\d+)/diagnostic/create/$', patients_views.create_diagnostic,
        name='create_diagnostic'),
    url(r'^patients/check/(?P<dni>\d+)/diagnostic/delete/(?P<code>\d+)/$', patients_views.delete_diagnostic,
        name='delete_diagnostic'),
    url(r'^patients/delete/(?P<dni>\d+)/$', patients_views.delete_patient, name='delete_patient'),
    # Treatments
    url(r'^treatments/$', treatments_views.index, name='treatments'),
    url(r'^treatments/create/$', treatments_views.create_treatment, name='create_treatment'),
    url(r'^treatments/edit/(?P<code>\w+)/$', treatments_views.edit_treatment, name='edit_treatment'),
    url(r'^treatments/delete/(?P<code>\w+)/$', treatments_views.delete_treatment, name='delete_treatment'),
    # Treatment sequence
    url(r'^sequences/$', sequences_views.index, name='sequences'),
    url(r'^sequences/create/$', sequences_views.create_sequence, name='create_sequence'),
    url(r'^sequences/process/(?P<code>\d+)/$', sequences_views.process_sequence, name='process_sequence'),
    url(r'^sequences/process/(?P<code>\d+)/treatment/delete/(?P<code2>\d+)/$',
        sequences_views.delete_sequence_treatment, name='delete_sequence_treatment'),
    url(r'^sequences/close/(?P<code>\d+)/$', sequences_views.close_sequence, name='close_sequence'),
    url(r'^sequences/cancel/(?P<code>\d+)/$', sequences_views.cancel_sequence, name='cancel_sequence'),
    url(r'^sequences/invoice/(?P<code>\d+)/$', sequences_views.invoice_sequence, name='invoice_sequence'),
]
