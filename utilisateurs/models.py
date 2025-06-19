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
    
    verification_code = models.CharField(max_length=6, null=True, blank=True)
    code_expires_at = models.DateTimeField(null=True, blank=True)  #  pour expiration

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nom', 'prenom']
    
    objects = UserManager()

    class Meta:
        db_table = 'utilisateurs_user' 

    def save(self, *args, **kwargs):
        # Pour le superuser, forcer le role admin
        if self.is_superuser:
            self.role = 'admin'
        super().save(*args, **kwargs)
        
        # Importer ici pour éviter les problEmes d'importation circulaire
        from .models import Patient, Docteur

        # Creation automatique du profil Patient/Docteur
        if self.role == 'patient' and not hasattr(self, 'patient'):
            Patient.objects.get_or_create(user=self)
        elif self.role == 'docteur' and not hasattr(self, 'docteur'):
            Docteur.objects.get_or_create(user=self)

    def get_initials(self):
        return f"{self.prenom[0]}{self.nom[0]}".upper()

   

# 2. Specialite
class Specialite(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.nom


# 3. Docteur
class Docteur(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialite = models.ForeignKey(Specialite, on_delete=models.SET_NULL, null=True)
    est_approuve = models.BooleanField(default=False)  # Approuve par l'admin

    def __str__(self):
        return f"Dr {self.user.nom} {self.user.prenom}"
    

    

# 4. Patient
class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.nom} {self.user.prenom}"
    
    