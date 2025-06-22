from django.contrib.auth.models import BaseUserManager
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _



from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


# 1. Utilisateur


class UserManager(BaseUserManager):

    def create_user(self, email, nom, prenom, password=None, **extra_fields):
        if not email:
            raise ValueError("L'email est requis")
        email = self.normalize_email(email)
        user = self.model(email=email, nom=nom, prenom=prenom, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nom, prenom, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        return self.create_user(email, nom, prenom, password, **extra_fields)

class User(AbstractUser):
    username = None
    email = models.EmailField('email address', unique=True)
    
    
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    is_doctor_request = models.BooleanField(default=False)
    role = models.CharField(
        max_length=20,
        choices=[('patient', 'Patient'), ('docteur', 'Docteur'), ('admin', 'Administrateur')],
        default='patient'
    )
    telephone = models.CharField(max_length=20, blank=True, null=True)
    date_naiss = models.DateField(null=True, blank=True)
    adresse = models.TextField(blank=True)
    genre = models.CharField(max_length=1, choices=[('M', 'Masculin'), ('F', 'Féminin'), ('O', 'Autre')], blank=True)
    verification_code = models.CharField(max_length=6, null=True, blank=True)
    code_expires_at = models.DateTimeField(null=True, blank=True)  #  pour expiration

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nom', 'prenom']
    
    objects = UserManager()

    class Meta:
        db_table = 'utilisateurs_user' 

    @property
    def docteur(self):
        """Propriete pour acceder au profil docteur de maniere coherente"""
        return self.docteur_profile
    
    @property
    def patient(self):
        """Propriete pour acceder au profil patient"""
        return self.patient_profile

    def save(self, *args, **kwargs):
        # Pour le superuser, forcer le role admin
        if self.is_superuser:
            self.role = 'admin'
        super().save(*args, **kwargs)
        
        # Creation automatique du profil
        if self.role == 'patient' and not hasattr(self, 'patient_profile'):
            Patient.objects.get_or_create(user=self)
        elif self.role == 'docteur' and not hasattr(self, 'docteur_profile'):
            Docteur.objects.get_or_create(user=self)

    def get_initials(self):
        return f"{self.prenom[0]}{self.nom[0]}".upper()

   

# 2. Specialite

class Specialite(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Specialite"
        verbose_name_plural = "Specialites"
        ordering = ['nom']
    
    def __str__(self):
        return self.nom
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.nom


# 3. Docteur
class Docteur(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='docteur_profile')
    specialite = models.ForeignKey(Specialite, on_delete=models.SET_NULL, null=True)
    est_approuve = models.BooleanField(default=False)  # Approuve par l'admin
    numero_licence = models.CharField(max_length=50, unique=True,null=True)
    bio = models.TextField(blank=True)
    experience = models.PositiveIntegerField(default=0)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Dr {self.user.nom} {self.user.prenom}"
    

    

# 4. Patient
class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    docteur_principal = models.ForeignKey(Docteur, on_delete=models.SET_NULL, 
                                        null=True, blank=True,
                                        related_name='patients')
    groupe_sanguin = models.CharField(max_length=10, blank=True)
    taille = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    poids = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    allergies = models.TextField(blank=True)
    antecedents = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user.nom} {self.user.prenom}"
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile' )
    groupe_sanguin = models.CharField(max_length=10, blank=True)
    taille = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    poids = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    allergies = models.TextField(blank=True)
    antecedents = models.TextField(blank=True)
    def __str__(self):
        return f"{self.user.nom} {self.user.prenom}"
    
    