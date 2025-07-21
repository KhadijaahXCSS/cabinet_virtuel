from rest_framework import serializers
from .models import RendezVous, CreneauHoraire

# Serializer pour le rendez-vous
class RendezVousSerializer(serializers.ModelSerializer):
    docteur = serializers.StringRelatedField()
    patient = serializers.StringRelatedField()
    creneau = serializers.StringRelatedField()
    titre = serializers.CharField(max_length=255, required=True)
    date = serializers.DateField(required=True)
    heure = serializers.TimeField(required=True)
    statut = serializers.ChoiceField(choices=RendezVous.STATUT_CHOICES, default='en_attente')
    lieu = serializers.CharField(max_length=255, required=True)

    class Meta:
        model = RendezVous
        fields = '__all__'  # Ou liste explicite des champs si nécessaire

    def create(self, validated_data):
        return RendezVous.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.docteur = validated_data.get('docteur', instance.docteur)
        instance.patient = validated_data.get('patient', instance.patient)
        instance.titre = validated_data.get('titre', instance.titre)
        instance.date = validated_data.get('date', instance.date)
        instance.heure = validated_data.get('heure', instance.heure)
        instance.statut = validated_data.get('statut', instance.statut)
        instance.lieu = validated_data.get('lieu', instance.lieu)
        instance.creneau = validated_data.get('creneau', instance.creneau)
        instance.save()
        return instance

# Serializer pour le creneau horaire
class CreneauHoraireSerializer(serializers.ModelSerializer):
    docteur = serializers.StringRelatedField()
    jour = serializers.CharField(max_length=10, required=True)
    heure_debut = serializers.TimeField(required=True)
    heure_fin = serializers.TimeField(required=True)
    disponible = serializers.BooleanField(default=True)

    class Meta:
        model = CreneauHoraire
        fields = '__all__'

    def create(self, validated_data):
        return CreneauHoraire.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.docteur = validated_data.get('docteur', instance.docteur)
        instance.jour = validated_data.get('jour', instance.jour)
        instance.heure_debut = validated_data.get('heure_debut', instance.heure_debut)
        instance.heure_fin = validated_data.get('heure_fin', instance.heure_fin)
        instance.disponible = validated_data.get('disponible', instance.disponible)
        instance.save()
        return instance