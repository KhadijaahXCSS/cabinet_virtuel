from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import RendezVous, CreneauHoraire
from .serializers import RendezVousSerializer, CreneauHoraireSerializer

class RendezVousViewSet(viewsets.ModelViewSet):
    """
    API endpoint qui permet de voir et modifier les rendez-vous
    """
    queryset = RendezVous.objects.all().order_by('date', 'heure')
    serializer_class = RendezVousSerializer
    permission_classes = [permissions.IsAuthenticated]  

    def perform_create(self, serializer):
        
        instance = serializer.save()
        
       
        
    def perform_update(self, serializer):
        instance = serializer.save()
        
       
        if 'statut' in serializer.validated_data:
            new_status = serializer.validated_data['statut']
           

class CreneauHoraireViewSet(viewsets.ModelViewSet):
    """
    API endpoint qui permet de voir et modifier les créneaux horaires
    """
    queryset = CreneauHoraire.objects.all().order_by('jour', 'heure_debut')
    serializer_class = CreneauHoraireSerializer
    permission_classes = [permissions.IsAuthenticated]  

    def get_queryset(self):
        """
        Optionnel: Filtrer les créneaux par docteur si un paramètre est fourni
        """
        queryset = super().get_queryset()
        docteur_id = self.request.query_params.get('docteur', None)
        
        if docteur_id is not None:
            queryset = queryset.filter(docteur__id=docteur_id)
            
        return queryset

    def perform_create(self, serializer):
        
        instance = serializer.save()
        
    def perform_update(self, serializer):
        instance = serializer.save()
       