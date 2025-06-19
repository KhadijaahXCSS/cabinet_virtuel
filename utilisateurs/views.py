
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.contrib.auth import login, logout
from .forms import RegisterForm, LoginForm
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
                        "Vérification compte médecin",
                        f"Votre code: {user.verification_code}",
                        "no-reply@votrecabinet.com",
                        [user.email],
                        fail_silently=False,
                    )
                    messages.info(request, "Code envoyé par email")
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




def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            # Si le docteur n'est pas encore vérifié, rediriger vers la page d'activation
            if hasattr(user, 'is_doctor_request') and user.is_doctor_request and not getattr(user, 'is_verified', True):
                return redirect('activer_medecin')
            login(request, user)
            # Redirection basée sur le rôle
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
        messages.error(request, "Une erreur est survenue lors du chargement des données.")
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
    if not hasattr(request.user, 'docteur'):
        return redirect('index')
    
    today = timezone.now().date()
    
    # Rendez-vous du jour
    today_rdv = RendezVous.objects.filter(
        docteur=request.user.docteur,
        date=today
    ).order_by('heure')
    
    # Prochain RDV
    next_rdv = RendezVous.objects.filter(
        docteur=request.user.docteur,
        date__gte=today
    ).order_by('date', 'heure').first()
    
    # Statistiques
    monthly_rdv = RendezVous.objects.filter(
        docteur=request.user.docteur,
        date__month=today.month,
        date__year=today.year
    ).count()
    
    completed_rdv = RendezVous.objects.filter(
        docteur=request.user.docteur,
        statut='confirme',
        date__month=today.month,
        date__year=today.year
    ).count()
    
    # Creneaux disponibles
    available_slots = CreneauHoraire.objects.filter(
        docteur=request.user.docteur,
        disponible=True,
        jour__gte=today
    ).order_by('jour', 'heure_debut')
    
    context = {
        'today_rdv': today_rdv,
        'next_rdv': next_rdv,
        'monthly_rdv': monthly_rdv,
        'completed_rdv': completed_rdv,
        'available_slots': available_slots,
        'specialite': request.user.docteur.specialite,
    }
    
    return render(request, 'dashboard/docteur_dashboard.html', context)
    today = timezone.now().date()
    docteur = request.user.docteur
    
    context = {
        'today_rdv': RendezVous.objects.filter(
            docteur=docteur,
            date=today,
            statut='confirme'  # Utilisez 'confirme' comme défini dans models.py
        ).order_by('heure'),
        
        'pending_rdv': RendezVous.objects.filter(
            docteur=docteur,
            date__gte=today,
            statut='en_attente'
        ).count(),
        
        'specialite': docteur.specialite
    }
    return render(request, 'dashboard/docteur_dashboard.html', context)



@user_passes_test(lambda u: u.is_superuser)
def admin__patients(request):
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
        'search_query': search_query
    }
    return render(request, 'admin/patients_liste.html', context)


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



