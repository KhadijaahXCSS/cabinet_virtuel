from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [

    #Authentification
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    path('admed_dashboard/approuve_docteur/<int:docteur_id>/', views.approuve_docteur, name='approuve_docteur'),
    path('activer_docteur/', views.activer_docteur, name='activer_docteur'),
    
    path('activer_docteur/<int:docteur_id>/', views.activer_docteur, name='activer_docteur_id'),
    
    path('admed_dashboard/doctor-requests/<int:docteur_id>/approuve/', views.activer_docteur, name='approuve_docteur_request'),
   
   # Dashboard
    path('dashboard/', login_required(views.dashboard_redirect),  name='dashboard_redirect'),
    path('dashboard/patient/', views.patient_dashboard, name='patient_dashboard'),
    path('dashboard/docteur/', views.docteur_dashboard, name='docteur_dashboard'),
    path('dashboard/admin/', views.dashboard_admin, name='admed_dashboard'),
   
   
     # Admin
    path('admin/patients/', views.admin__patients, name='admin_patients_list'),
    path('admin/patients/<int:patient_id>/', views.patient_detail, name='admin_patient_detail'),
    
    # Docteur
    path('docteur/patients/', views.docteur__patients, name='docteur_patients_list'),
    path('docteur/patients/<int:patient_id>/', views.patient_detail, name='docteur_patient_detail'),


    # Profile
    #path('profile/', views.profile_view, name='profile'),
   # path('profile/docteur/', views.docteur_profile, name='docteur_profile'),
    #path('profile/patient.', views.patient_profile, name='patient_profile'),
    #path('profile/admin/', views.admin_profile, name='admin_profile'),
    


   
]

   