
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.contrib.auth import login as django_login, logout
from .forms import RegisterForm, LoginForm, AdminProfileForm, ProfileUpdateForm, DoctorProfileForm, PatientProfileForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.contrib.auth import get_user_model
from rendez_vous.models import RendezVous,CreneauHoraire
from .models import Docteur, Patient,Specialite
from datetime import date
from django.core.mail import send_mail
import random
from django.conf import settings
from django.db.models import Q



from .forms import SpecialiteForm









# Create your views here.




def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            
            if form.cleaned_data.get('demande_medecin'):
                user.role = 'docteur'
                user.is_active = False
                user.verification_code = str(random.randint(100000, 999999))
                user.code_expires_at = timezone.now() + timezone.timedelta(hours=24)  # Expire dans 24h
                
                try:
                    send_mail(
                        "Verification compte medecin",
                        f"Votre code: {user.verification_code}",
                        "no-reply@votrecabinet.com",
                        [user.email],
                        fail_silently=False,
                    )
                    messages.info(request, "Code envoyd par email")
                except:
                    messages.warning(request, f"Erreur d'envoi. Notez ce code: {user.verification_code}")
            
            user.save()
            return redirect('login')
    
    else:
        form = RegisterForm()
    return render(request, 'utilisateurs/register.html', {'form': form})
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            
            if form.cleaned_data.get('demande_medecin'):
                user.role = 'docteur'
                user.is_active = False  # Desactive jusqu'a validation admin
                code = str(random.randint(100000, 999999))
                user.verification_code = code

                # Envoi du code (adapte pour les modes dev/prod)
                try:
                    send_mail(
                        "Vérification de votre compte médecin",
                        f"Votre code de vérification est : {code}",
                        settings.DEFAULT_FROM_EMAIL or "no-reply@votrecabinet.com",
                        [user.email],
                        fail_silently=False,
                    )
                    if settings.DEBUG:
                        messages.info(request, f"[MODE TEST] Code de vérification : {code} (voir console)")
                    else:
                        messages.success(request, "Un code a été envoyé à votre email.")
                except Exception as e:
                    # Fallback si l'envoi échoue (affiche le code dans l'interface)
                    messages.warning(request, f"Erreur d'envoi. Notez ce code : {code}")
            
            user.save()
            return redirect('login')
    
    else:
        form = RegisterForm()
    return render(request, 'utilisateurs/register.html', {'form': form})
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            
            # Utilisez form.cleaned_data pour acceder au champ demande_medecin
            if form.cleaned_data.get('demande_medecin'):
                user.role = 'docteur'  # definir le role comme docteur
                user.is_active = False  # desactiver le compte jusqu'e validation
                
                # Generer et envoyer le code de verification
                code = str(random.randint(100000, 999999))
                user.verification_code = code
                
                send_mail(
                    "Vérification de votre compte médecin",
                    f"Votre code de vérification est : {code}",
                    "no-reply@votrecabinet.com",
                    [user.email],
                    fail_silently=False,
                )
                messages.info(request, "Un code de verification a ete envoye à votre email.")
            else:
                user.role = 'patient'  # Definir le role comme patient
            
            user.save()
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'utilisateurs/register.html', {'form': form})




def login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            # Si le docteur n'est pas encore verifie, rediriger vers la page d'activation
            if hasattr(user, 'is_doctor_request') and user.is_doctor_request and not getattr(user, 'is_verified', True):
                return redirect('activer_medecin')
            django_login(request, user)
            # Redirection basee sur le role
            if user.role == 'patient':
                return redirect('patient_dashboard')
            elif user.role == 'docteur':
                return redirect('docteur_dashboard')
            elif user.is_superuser:
                return redirect('admed_dashboard')
            else:
                return redirect('index')  
    else:
        form = LoginForm()
    return render(request, 'utilisateurs/login.html', {'form': form})
    

def logout_view(request):
    logout(request)
    return redirect('login')



def is_admin(user):
    return user.is_superuser or user.is_staff

@user_passes_test(is_admin)
def dashboard_admin(request):
    User = get_user_model()
    
    try:
        # Statistiques principales
        total_users = User.objects.count()
        total_patients = Patient.objects.count()
        total_doctors = Docteur.objects.filter(est_approuve=True).count()
        pending_doctors = Docteur.objects.filter(est_approuve=False).count()
        total_rdv = RendezVous.objects.count()
        
        # Rendez-vous du jour avec optimisation des requetes
        today_rdv = RendezVous.objects.filter(date=date.today()).select_related(
            'patient__user', 
            'docteur__user'
        ).order_by('heure')

        # Activites recentes avec pagination implicite
        latest_users = User.objects.order_by('-date_joined')[:5]
        latest_rdv = RendezVous.objects.select_related(
            'patient__user',
            'docteur__user'
        ).order_by('-date', '-heure')[:5]

        # Calcul des stats supplementaires
        rdv_this_month = RendezVous.objects.filter(
            date__month=date.today().month,
            date__year=date.today().year
        ).count()

        context = {
            # Statistiques de base
            'total_users': total_users,
            'total_patients': total_patients,
            'total_doctors': total_doctors,
            'pending_doctors': pending_doctors,
            'total_rdv': total_rdv,
            'rdv_this_month': rdv_this_month,
            
            # Listes
            'today_rdv': today_rdv,
            'latest_users': latest_users,
            'latest_rdv': latest_rdv,
            
            # Specialites
            'specialites': Specialite.objects.all(),
            
            # Pour les templates
            'current_date': date.today(),
              'pending_doctors_list': Docteur.objects.filter(est_approuve=False).select_related('user')[:5],
        }
       

    except Exception as e:
        # Gestion des erreurs pour le debogage
        if settings.DEBUG:
            raise e
        messages.error(request, "Une erreur est survenue lors du chargement des donnees.")
        context = {}

    return render(request, 'dashboard/admed_dashboard.html', context)


@user_passes_test(lambda u: u.is_superuser)
def approuve_docteur(_request, docteur_id):
    docteur = Docteur.objects.get(pk=docteur_id)
    docteur.est_approuve = True
    docteur.user.is_active = True  # Activer le compte
    docteur.user.save()
    docteur.save()
    # Envoyer un email de confirmation au docteur
    send_mail(
        "Votre compte a ete approuve",
        "Vous pouvez maintenant vous connecter.",
        "no-reply@votrecabinet.com",
        [docteur.user.email],
    )
    return redirect('admed_dashboard')

def activer_docteur(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        if request.user.verification_code == code:
            request.user.is_verified = True
            request.user.save()
            return redirect('docteur_dashboard')
        else:
            messages.error(request, "Code invalide.")
    return render(request, 'utilisateurs/activation_docteur.html')



@login_required
def dashboard_redirect(request):
    if request.user.role == 'patient':
        return redirect('patient_dashboard')
    elif request.user.role == 'docteur':
        return redirect('docteur_dashboard')
    elif request.user.is_superuser:
        return redirect('admed_dashboard')
    else:
        return redirect('login')






def is_patient(user):
    return user.role == 'patient'

def is_doctor(user):
    return user.role == 'docteur'




@login_required
@user_passes_test(lambda u: u.role == 'patient')
def patient_dashboard(request):
    patient = request.user.patient
    today = timezone.now().date()
    
    context = {
        'next_rdv': RendezVous.objects.filter(
            patient=patient,
            date__gte=today,
            statut='confirme'
        ).order_by('date', 'heure').first(),
        
        'recent_rdvs': RendezVous.objects.filter(
            patient=patient
        ).order_by('-date', '-heure')[:5],
        
        'total_rdv': RendezVous.objects.filter(
            patient=patient
        ).count(),
        
        'rdv_confirmed': RendezVous.objects.filter(
            patient=patient,
            statut='confirme'
        ).count(),
        
        'main_doctor': patient.docteur if hasattr(patient, 'docteur') else None
    }
    return render(request, 'dashboard/patient_dashboard.html', context)


@login_required
@user_passes_test(lambda u: u.role == 'docteur')
def docteur_dashboard(request):
    if not hasattr(request.user, 'docteur_profile'):
        messages.error(request, "Profil docteur non configuré")
        return redirect('docteur_profile')
    
    docteur = request.user.docteur_profile
    today = timezone.now().date()
    
    context = {
        'today_rdv': RendezVous.objects.filter(
            docteur=docteur,
            date=today,
            statut='confirme'
        ).order_by('heure'),
        'pending_rdv': RendezVous.objects.filter(
            docteur=docteur,
            date__gte=today,
            statut='en_attente'
        ).count(),
        'specialite': docteur.specialite,
        'docteur': docteur
    }
    return render(request, 'dashboard/docteur_dashboard.html', context)



@login_required
@user_passes_test(lambda u: u.role == 'docteur')
def docteur__patients(request):
    
    patients = Patient.objects.filter(
       rendez_vous__docteur=request.user.docteur
    ).distinct().select_related('user')
    
    context = {
        'patients': patients
    }
    return render(request, 'docteur/patients_liste.html', context)

@login_required
def patient_detail(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    
    
    if request.user.role == 'docteur':
        if not RendezVous.objects.filter(docteur=request.user.docteur, patient=patient).exists():
            raise PermissionDenied
    elif request.user.role != 'admin':
        raise PermissionDenied
    
    rdvs = RendezVous.objects.filter(patient=patient).order_by('-date')
    
    if request.user.role == 'docteur':
        rdvs = rdvs.filter(docteur=request.user.docteur)
    
    context = {
        'patient': patient,
        'rdvs': rdvs[:5],  
        'total_rdvs': rdvs.count()
    }
    
    return render(request, 'patients/patient_detail.html', context)




@login_required
def profile_view(request):
    user = request.user
    
    if user.role == 'admin':
        return admin_profile(request)
    elif user.role == 'docteur':
        return docteur_profile(request)
    elif user.role == 'patient':
        return patient_profile(request)
    else:
        return redirect('index')

@login_required
@user_passes_test(lambda u: u.role == 'admin')
def admin_profile(request):
    if request.method == 'POST':
        form = AdminProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil mis à jour avec succès")
            return redirect('admin_profile')
    else:
        form = AdminProfileForm(instance=request.user)
    
    context = {
        'form': form,
        'profile_data': {
            'full_name': f"{request.user.prenom} {request.user.nom}",
            'email': request.user.email,
            'role': request.user.get_role_display(),
            'phone': request.user.telephone if hasattr(request.user, 'telephone') else None,
            'date_joined': request.user.date_joined.strftime("%d/%m/%Y")
        },
        'stats': {
            'total_patients': Patient.objects.count(),
            'total_doctors': Docteur.objects.filter(est_approuve=True).count(),
            'pending_doctors': Docteur.objects.filter(est_approuve=False).count()
        }
    }
    return render(request, 'profile/admin_profile.html', context)



@login_required
@user_passes_test(lambda u: u.role == 'docteur')
def docteur_profile(request):
    docteur = request.user.docteur_profile
    
    if request.method == 'POST':
        # Formulaire user (informations de base)
        user_form = ProfileUpdateForm(request.POST, instance=request.user)
        # Formulaire docteur (informations professionnelles)
        doctor_form = DoctorProfileForm(request.POST, instance=docteur)
        
        if user_form.is_valid() and doctor_form.is_valid():
            user_form.save()
            doctor_form.save()
            messages.success(request, "Profil mis à jour avec succes")
            return redirect('docteur_profile')
    else:
        user_form = ProfileUpdateForm(instance=request.user)
        doctor_form = DoctorProfileForm(instance=docteur)
    specialites = Specialite.objects.all()
    
    context = {
        'user_form': user_form,
        'doctor_form': doctor_form,
        'specialites': specialites, 
        'profile_data': {
            'full_name': f"{request.user.prenom} {request.user.nom}",
            'nom': request.user.nom,
            'prenom': request.user.prenom,
            'email': request.user.email,
            'telephone': request.user.telephone,
            'specialite': docteur.specialite.nom if docteur.specialite else "Non specifie",
            'numero_licence': docteur.numero_licence,
            'bio': docteur.bio,
            'experience': docteur.experience,
            'consultation_fee': docteur.consultation_fee,
            'est_approuve': docteur.est_approuve,
            'profile_picture': request.user.profile_picture.url if hasattr(request.user, 'profile_picture') and request.user.profile_picture else None
        },
        'stats': {
            'rdv_today': RendezVous.objects.filter(
                docteur=docteur, 
                date=timezone.now().date()
            ).count(),
            'rdv_month': RendezVous.objects.filter(
                docteur=docteur,
                date__month=timezone.now().month
            ).count(),
            'available_slots': CreneauHoraire.objects.filter(
                docteur=docteur,
                disponible=True,
                jour__gte=timezone.now().date()
            ).count()
        }
    }
    return render(request, 'profile/docteur_profile.html', context)



@login_required
@user_passes_test(lambda u: u.role == 'patient')
def patient_profile(request):
    patient = request.user.patient_profile
    
    if request.method == 'POST':
        user_form = ProfileUpdateForm(request.POST, instance=request.user)
        patient_form = PatientProfileForm(request.POST, instance=patient)
        
        if user_form.is_valid() and patient_form.is_valid():
            user_form.save()
            
            # Gestion spécifique pour docteur_principal si le champ existe
            if hasattr(patient, 'docteur_principal'):
                patient.docteur_principal = patient_form.cleaned_data.get('docteur_principal')
                patient.save()
            else:
                patient_form.save()
                
            messages.success(request, "Profil mis à jour avec succès")
            return redirect('patient_profile')
    else:
        user_form = ProfileUpdateForm(instance=request.user)
        patient_form = PatientProfileForm(instance=patient)
    
    context = {
        'user_form': user_form,
        'patient_form': patient_form,
        'profile_data': {
            'full_name': f"{request.user.prenom} {request.user.nom}",
            'email': request.user.email,
            'phone': request.user.telephone,
            'address': request.user.adresse if hasattr(request.user, 'adresse') else None,
            'birth_date': request.user.date_naiss if hasattr(request.user, 'date_naiss') else None,
            'gender': request.user.genre if hasattr(request.user, 'genre') else None,
            'blood_group': patient.groupe_sanguin,
            'height': patient.taille,
            'weight': patient.poids,
            'allergies': patient.allergies,
            'antecedents': patient.antecedents,
             'main_doctor': patient.docteur_principal,
            'profile_picture': request.user.profile_picture.url if hasattr(request.user, 'profile_picture') else None
        },
       'stats': {
            'total_rdv': RendezVous.objects.filter(patient=patient).count(),
            'upcoming_rdv': RendezVous.objects.filter(
                patient=patient,
                date__gte=timezone.now().date()
            ).count(),
            'past_rdv': RendezVous.objects.filter(
                patient=patient,
                date__lt=timezone.now().date()
            ).count()
        }
    }
    return render(request, 'profile/patient_profile.html', context)
        
    


@user_passes_test(lambda u: u.is_superuser)
def admin_docteurs(request):
    docteurs = Docteur.objects.all().select_related('user', 'specialite')
    
    # Filtres
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    if search_query:
        docteurs = docteurs.filter(
            Q(user__nom__icontains=search_query) |
            Q(user__prenom__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(specialite__nom__icontains=search_query)
        )
    
    if status_filter in ['approved', 'pending']:
        docteurs = docteurs.filter(est_approuve=(status_filter == 'approved'))
    
    context = {
        'docteurs': docteurs,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    return render(request, 'admin/docteur_liste.html', context)


@user_passes_test(lambda u: u.is_superuser)
def admin_patients(request):
    patients = Patient.objects.all().select_related('user')
    
    # Filtres
    search_query = request.GET.get('search', '')
    if search_query:
        patients = patients.filter(
            Q(user__nom__icontains=search_query) |
            Q(user__prenom__icontains=search_query) |
            Q(user__email__icontains=search_query)
        )
    
    context = {
        'patients': patients,
        'search_query': search_query,
        'total_patients': patients.count()
    }
    return render(request, 'admin/patients_liste.html', context)





@login_required
@user_passes_test(lambda u: u.role == 'admin')
def admin_specialites(request):
    specialites = Specialite.objects.all().order_by('nom')
    return render(request, 'admin/specialites/list.html', {'specialites': specialites})

@login_required
@user_passes_test(lambda u: u.role == 'admin')
def admin_add_specialite(request):
    if request.method == 'POST':
        form = SpecialiteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Spécialité ajoutée avec succès")
            return redirect('admin_specialites')
    else:
        form = SpecialiteForm()
    return render(request, 'admin/specialites/add.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.role == 'admin')
def admin_edit_specialite(request, pk):
    specialite = get_object_or_404(Specialite, pk=pk)
    if request.method == 'POST':
        form = SpecialiteForm(request.POST, instance=specialite)
        if form.is_valid():
            form.save()
            messages.success(request, "Spécialité mise à jour")
            return redirect('admin_specialites')
    else:
        form = SpecialiteForm(instance=specialite)
    return render(request, 'admin/specialites/edit.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.role == 'admin')
def admin_delete_specialite(request, pk):
    specialite = get_object_or_404(Specialite, pk=pk)
    if request.method == 'POST':
        specialite.delete()
        messages.success(request, "Spécialité supprimée")
        return redirect('admin_specialites')
    return render(request, 'admin/specialites/delete.html', {'specialite': specialite})


@login_required
def admin_supervision_rdv(request):
    if request.user.role != 'admin':
        return redirect('index')
    
    # Recuperer tous les rendez-vous avec les relations necessaires
    rdvs = RendezVous.objects.all().select_related(
        'docteur__user', 
        'patient__user',
        'docteur__specialite'
    ).order_by('-date', '-heure')
    
    # Filtres possibles
    statut = request.GET.get('statut')
    docteur_id = request.GET.get('docteur')
    date = request.GET.get('date')
    
    if statut in dict(RendezVous.STATUT_CHOICES).keys():
        rdvs = rdvs.filter(statut=statut)
    
    if docteur_id:
        rdvs = rdvs.filter(docteur__id=docteur_id)
    
    if date:
        rdvs = rdvs.filter(date=date)
    
    # Liste des docteurs pour le filtre
    docteurs = Docteur.objects.filter(user__is_active=True, est_approuve=True)
    
    return render(request, 'admin/supervision_rdv.html', {
        'rdvs': rdvs,
        'statut_choices': RendezVous.STATUT_CHOICES,
        'docteurs': docteurs
    })




