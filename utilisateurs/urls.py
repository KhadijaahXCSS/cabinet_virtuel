from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [

    #Authentification
    path('register/', views.register_view, name='register'),
    path('login/', views.login, name='login'),
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
    path('dashboard/admin/patients/', views.admin_patients, name='admin_patients_list'),
    path('dashboard/admin/docteurs/', views.admin_docteurs, name='admin_docteurs_list'),
     path('dashboard/admin/supervision-rdv/', views.admin_supervision_rdv, name='admin_supervision_rdv'),
    

    # Docteur
    path('docteur/patients/', views.docteur__patients, name='docteur_patients_list'),
    path('docteur/patients/<int:patient_id>/', views.patient_detail, name='docteur_patient_detail'),
    


    # Profile
    path('profile/', views.profile_view, name='profile'),
    path('profile/docteur/', views.docteur_profile, name='docteur_profile'),
    path('profile/patient.', views.patient_profile, name='patient_profile'),
    path('profile/admin/', views.admin_profile, name='admin_profile'),
    
    # Specialites
    path('dashboard/admin/specialites/', views.admin_specialites, name='admin_specialites'),
    path('dashboard/admin/specialites/ajouter/', views.admin_add_specialite, name='admin_add_specialite'),
    path('dashboard/admin/specialites/<int:pk>/modifier/', views.admin_edit_specialite, name='admin_edit_specialite'),
    path('dashboard/admin/specialites/<int:pk>/supprimer/', views.admin_delete_specialite, name='admin_delete_specialite'),
   
]

   