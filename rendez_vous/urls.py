
from django.urls import path
from .views import (
    home, demander_rendezvous, liste_rendezvous_docteur,confirmer_rendezvous, refuser_rendezvous, liste_rendezvous_patient, detail_rendezvous,
    supprimer_rendezvous, PlanningDocteurView, CreneauCreateView,  CreneauUpdateView, CreneauDeleteView
)

urlpatterns = [
    path('', home, name='index'),
    path('demander-rendezvous/', demander_rendezvous, name='demander_rendezvous'),
    path('liste-rendezvous-patient/', liste_rendezvous_patient, name='liste_rendezvous_patient'),
    path('liste-rendezvous-medecin/', liste_rendezvous_docteur, name='liste_rendezvous_docteur'),
    
    path('rendezvous/<int:pk>/', detail_rendezvous, name='detail_rendezvous'),
    path('rendezvous/<int:pk>/supprimer/', supprimer_rendezvous, name='supprimer_rendezvous'),
    path('rendezvous/<int:pk>/confirmer/', confirmer_rendezvous, name='confirmer_rendezvous'),
    path('rendezvous/<int:pk>/refuser/', refuser_rendezvous, name='refuser_rendezvous'),

    path('planning/', PlanningDocteurView.as_view(), name='planning_docteur'),
    path('planning/creneau/ajouter/', CreneauCreateView.as_view(), name='creneau_ajouter'),
    path('planning/creneau/<int:pk>/modifier/', CreneauUpdateView.as_view(), name='creneau_modifier'),
    path('planning/creneau/<int:pk>/supprimer/', CreneauDeleteView.as_view(), name='creneau_supprimer'),
]