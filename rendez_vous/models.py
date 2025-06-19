
from django.db import models
from django.core.exceptions import ValidationError

from utilisateurs.models import Docteur, Patient





# Create your models here.

class RendezVous(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('confirme', 'Confirmé'),
        ('refuse', 'Refusé'),
        ('annule', 'Annulé')
    ]

    docteur = models.ForeignKey(Docteur, on_delete=models.CASCADE, related_name='rendez_vous')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='rendez_vous')
    titre = models.CharField(max_length=255)
    creneau = models.ForeignKey('CreneauHoraire', on_delete=models.CASCADE, null=True, blank=True)  
    date = models.DateField()  #  conserver pour compatibilite
    heure = models.TimeField()  # conserver pour compatibilite
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='en_attente'
    )
    lieu = models.CharField(max_length=255, verbose_name="Lieu du rendez-vous")

    def save(self, *args, **kwargs):
        # Met a jour la date et l'heure si un creneau est specifie
        if self.creneau:
            self.date = self.creneau.jour
            self.heure = self.creneau.heure_debut
            # Marque le crwneau comme indisponible
            self.creneau.disponible = False
            self.creneau.save()
        super().save(*args, **kwargs)

    def clean(self):
        if self.creneau:
            
            if not self.creneau.disponible:
                raise ValidationError("Ce creneau n'est plus disponible")
            
           
            if self.creneau.docteur != self.docteur:
                raise ValidationError("Ce creneau ne correspond pas au docteur selectionne")
        else:
           
            conflits = RendezVous.objects.filter(
                docteur=self.docteur,
                date=self.date,
                heure=self.heure
            ).exclude(pk=self.pk)  
            
            if conflits.exists():
                raise ValidationError("Le docteur a deja un rendez-vous à ce creneau.")
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('confirme', 'Confirmé'),
        ('refuse', 'Refusé'),
        ('annule', 'Annulé')
    ]

    docteur = models.ForeignKey(Docteur, on_delete=models.CASCADE, related_name='rendez_vous')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='rendez_vous')
    titre = models.CharField(max_length=255)
    date = models.DateField()
    heure = models.TimeField()
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='en_attente'
    )
    lieu = models.CharField(max_length=255, verbose_name="Lieu du rendez-vous")

    def clean(self):
        
        conflits = RendezVous.objects.filter(
            docteur=self.docteur,
            date=self.date,
            heure=self.heure
        ).exclude(pk=self.pk)  
        
        if conflits.exists():
            raise ValidationError("Le docteur a deja un rendez-vous à ce creneau.")
    
    def confirmer(self):
        self.statut = 'confirme'
        self.save()
    
    def refuser(self):
        self.statut = 'refuse'
        self.save()

    class Meta:
        ordering = ['date', 'heure']
        verbose_name_plural = "Rendez-vous"

    def __str__(self):
        return f"{self.titre} - {self.date} {self.heure}"
    



class CreneauHoraire(models.Model):
    docteur = models.ForeignKey(Docteur, on_delete=models.CASCADE, related_name='creneaux')
    jour = models.DateField()
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()
    disponible = models.BooleanField(default=True)

    class Meta:
        ordering = ['jour', 'heure_debut']
        unique_together = ['docteur', 'jour', 'heure_debut']

    def __str__(self):
        return f"{self.docteur} - {self.jour} {self.heure_debut}-{self.heure_fin}"

    def clean(self):
        if self.heure_debut >= self.heure_fin:
            raise ValidationError("L'heure de fin doit etre apres l'heure de debut")
        
        # Verifier les chevauchements
        chevauchements = CreneauHoraire.objects.filter(
            docteur=self.docteur,
            jour=self.jour,
            heure_debut__lt=self.heure_fin,
            heure_fin__gt=self.heure_debut
        ).exclude(pk=self.pk if self.pk else None)
        
        if chevauchements.exists():
            raise ValidationError("Ce creneau chevauche un autre creneau existant")