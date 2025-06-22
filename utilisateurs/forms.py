from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.db import models
from django.utils.translation import gettext_lazy as _
from .models import User, Docteur, Patient, Specialite



class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Mot de passe")
    confirmer_password = forms.CharField(widget=forms.PasswordInput, label="Confirmer le mot de passe")
    demande_medecin = forms.BooleanField(
        required=False,
        label="je suis un docteur du cabinet et je souhaite m'inscrire",
    )

    class Meta:
        model = User
        fields = ['nom', 'prenom', 'email'] 

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirmer_password = cleaned_data.get('confirmer_password')
        
        if password and confirmer_password and password != confirmer_password:
            self.add_error('confirmer_password', "Les mots de passe ne correspondent pas.")
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if self.cleaned_data['demande_medecin']:
            user.role = 'docteur'
            user.is_active = False  # Desactiver jusqu'a validation
        else:
            user.role = 'patient'
        if commit:
            user.save()
        return user

class LoginForm(AuthenticationForm):
    username = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Mot de passe")

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['nom', 'prenom', 'email', 'telephone', 'date_naiss', 'adresse', 'genre']
        widgets = {
            'date_naiss': forms.DateInput(attrs={'type': 'date'}),
            'adresse': forms.Textarea(attrs={'rows': 3}),
            'genre': forms.Select(choices=[('M', 'Masculin'), ('F', 'Féminin'), ('O', 'Autre')])
        }

        
#Admin
class AdminProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['nom', 'prenom', 'email', 'telephone']
        widgets = {
            'telephone': forms.TextInput(attrs={'placeholder': 'Numero de téléphone'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].disabled = True  # L'email ne peut pas etre modifie


#Docteur
class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = Docteur
        fields = ['specialite', 'numero_licence', 'bio', 'experience', 'consultation_fee']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personnalisation des champs si necessaire
        self.fields['consultation_fee'].widget.attrs.update({'step': '0.01'})




# Patient
class PatientProfileForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['docteur_principal', 'groupe_sanguin', 'taille', 'poids', 'allergies', 'antecedents']
        widgets = {
            'allergies': forms.Textarea(attrs={'rows': 3}),
            'antecedents': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if 'docteur_principal' not in self.fields and hasattr(self.Meta.model, 'docteur_principal'):
            self.fields['docteur_principal'] = forms.ModelChoiceField(
                queryset=Docteur.objects.filter(est_approuve=True),
                required=False,
                label="Médecin traitant"
            )

# Specialite

class SpecialiteForm(forms.ModelForm):
    class Meta:
        model = Specialite
        fields = ['nom', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-textarea'}),
        }
        labels = {
            'nom': "Nom de la spécialite",
            'description': "Description"
        }