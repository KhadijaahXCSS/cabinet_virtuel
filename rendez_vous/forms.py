from django import forms
from .models import RendezVous
from utilisateurs.models import Docteur
from .models import CreneauHoraire
from django.utils import timezone

class DemandeRendezVousForm(forms.ModelForm):
    creneau = forms.ModelChoiceField(
        queryset=CreneauHoraire.objects.filter(disponible=True, jour__gte=timezone.now().date()),
        required=True,
        label="Creneau disponible",
        widget=forms.Select(attrs={'class': 'w-full p-2 border border-gray-300 rounded-lg'})
    )

    class Meta:
        model = RendezVous
        fields = ['titre', 'docteur', 'creneau', 'lieu']
        widgets = {
            'docteur': forms.Select(attrs={'class': 'w-full p-2 border border-gray-300 rounded-lg'}),
            'statut': forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Formatage de l'affichage des creneaux
        self.fields['creneau'].label_from_instance = lambda obj: (
            f"{obj.jour.strftime('%d/%m/%Y')} - {obj.heure_debut.strftime('%H:%M')} à {obj.heure_fin.strftime('%H:%M')}"
        )
        # Filtre les docteurs actifs et approuves
        self.fields['docteur'].queryset = Docteur.objects.filter(
            user__is_active=True,
            est_approuve=True
        ).select_related('user', 'specialite')
        
        # Formatage de l'affichage des docteurs dans le select
        self.fields['docteur'].label_from_instance = lambda obj: (
            f"Dr {obj.user.nom} {obj.user.prenom} ({obj.specialite.nom if obj.specialite else 'Non spécifié'})"
        )
        
        
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full p-2 border border-gray-300 rounded-lg'
            })





class CreneauHoraireForm(forms.ModelForm):
    class Meta:
        model = CreneauHoraire
        fields = ['jour', 'heure_debut', 'heure_fin']
        widgets = {
            'jour': forms.DateInput(attrs={'type': 'date', 'min': timezone.now().date()}),
            'heure_debut': forms.TimeInput(attrs={'type': 'time'}),
            'heure_fin': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        self.docteur = kwargs.pop('docteur', None)
        super().__init__(*args, **kwargs)
        
    def clean(self):
        cleaned_data = super().clean()
        if self.docteur:
            self.instance.docteur = self.docteur
        return cleaned_data