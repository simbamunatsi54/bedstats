from django.contrib import admin
from django.urls import path
from beds import views
from django.contrib.auth import views as auth_views


urlpatterns = [

    path(
        'admin/',
        admin.site.urls
    ),

    # Dashboard
    path(
        '',
        views.dashboard,
        name='dashboard'
    ),

    # Bed Management
    path(
        'beds/',
        views.bed_list,
        name='bed_list'
    ),

    path(
        'beds/<int:bed_id>/status/',
        views.change_bed_status,
        name='change_bed_status'
    ),

    # Patient Management
    path(
        'patients/',
        views.patient_list,
        name='patient_list'
    ),

    path(
        'patients/register/',
        views.register_patient,
        name='register_patient'
    ),
    path(
        'admissions/new/',
        views.admission_create,
        name='admission_create'
    ),
    path(
        'discharges/new/',
        views.discharge_create,
        name='discharge_create'
    ),
    path(
        'transfers/new/',
        views.transfer_create,
        name='transfer_create'
    ),
    path(
        'deaths/new/',
        views.death_create,
        name='death_create'
    ),
    path(
        'reports/',
        views.reports,
        name='reports'
    ),
    path(
        'reports/excel/',
        views.export_excel,
        name='export_excel'
    ),
    path(
        'reports/pdf/',
        views.export_pdf,
        name='export_pdf'
    ),
    path(
        'login/',
         auth_views.LoginView.as_view(
        template_name='registration/login.html'
    ),
    name='login'
    ),

    path(
    'logout/',
    auth_views.LogoutView.as_view(),
    name='logout'
    ),
    path(
        'logout/',
        auth_views.LogoutView.as_view(),
        name='logout',
    ),
    path(
        'patient-movement/',
        views.patient_movement,
        name='patient_movement'
    ),

]
handler403 = 'beds.views.custom_permission_denied'