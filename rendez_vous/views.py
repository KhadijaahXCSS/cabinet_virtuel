
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import DemandeRendezVousForm
from .models import RendezVous
from utilisateurs.models import Patient, Docteur

from django.contrib import messages
from django.utils import timezone


from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import CreneauHoraire
from .forms import CreneauHoraireForm

# Create your views here.

def home(request):
    
  

    return render(request, 'pages/index.html')


@login_required
def demander_rendezvous(request):
    if request.user.role != 'patient':
        return redirect('index')  

    patient = Patient.objects.get(user=request.user)

    if request.method == 'POST':
        form = DemandeRendezVousForm(request.POST)
        if form.is_valid():
            rdv = form.save(commit=False)
            rdv.patient = patient
            rdv.statut = 'en_attente'
            
           
            if rdv.creneau:
                rdv.date = rdv.creneau.jour
                rdv.heure = rdv.creneau.heure_debut
            
            rdv.save()
            return redirect('patient_dashboard')
    else:
        form = DemandeRendezVousForm()
    
    return render(request, 'rendezvous/demande.html', {'form': form})


@login_required
def liste_rendezvous_patient(request):
    if request.user.role != 'patient':
        return redirect('index')  

    patient = Patient.objects.get(user=request.user)
    rdvs = RendezVous.objects.filter(patient=patient).order_by('-date', '-heure')

    return render(request, 'rendezvous/liste_patient.html', {'rdvs': rdvs})

@login_required
def liste_rendezvous_docteur(request):
    if not hasattr(request.user, 'docteur'):
        return redirect('index')
    
    rdvs = RendezVous.objects.filter(
        docteur=request.user.docteur
    ).select_related('patient__user').order_by('date', 'heure')
    
    
    statut = request.GET.get('statut')
    if statut in dict(RendezVous.STATUT_CHOICES).keys():
        rdvs = rdvs.filter(statut=statut)
    
    return render(request, 'rendezvous/liste_medecin.html', {
        'rdvs': rdvs,
        'statut_choices': RendezVous.STATUT_CHOICES
    })



@login_required
def confirmer_rendezvous(request, pk):
    if request.user.role != 'docteur':
        return redirect('index')
    
    rdv = get_object_or_404(RendezVous, pk=pk, docteur__user=request.user)
    rdv.confirmer()
    messages.success(request, "Rendez-vous confirme.")
    return redirect('liste_rendezvous_docteur') 



@login_required
def refuser_rendezvous(request, pk):
    if request.user.role != 'docteur':
        return redirect('index')
    
    rdv = get_object_or_404(RendezVous, pk=pk, docteur__user=request.user)
    rdv.refuser()
    messages.success(request, "Rendez-vous refuse.")
    return redirect('liste_rendezvous_docteur') 




def detail_rendezvous(request, pk):
    rdv = get_object_or_404(RendezVous, pk=pk, patient__user=request.user)
    
    if request.method == 'POST':
        
        if 'annuler' in request.POST and rdv.statut == 'en_attente':
            rdv.statut = 'annule'
            rdv.save()
            messages.success(request, "Le rendez-vous a ete annule.")
            return redirect('liste_rendezvous_patient')
    
    return render(request, 'rendezvous/detail_rendezvous.html', {
        'rdv': rdv,
        'peut_annuler': rdv.statut == 'en_attente'
    })




@login_required
def supprimer_rendezvous(request, pk):
    rdv = get_object_or_404(RendezVous, pk=pk, patient__user=request.user)
    
    if request.method == 'POST':
        rdv.delete()
        messages.success(request, "Le rendez-vous a été supprimé.")
        return redirect('liste_rendezvous_patient')
    
    


class PlanningDocteurView(LoginRequiredMixin, ListView):
    model = CreneauHoraire
    template_name = 'docteur/planning_docteur.html'
    context_object_name = 'creneaux'

    def get_queryset(self):
        return CreneauHoraire.objects.filter(
            docteur=self.request.user.docteur
        ).order_by('jour', 'heure_debut')

class CreneauCreateView(LoginRequiredMixin, CreateView):
    model = CreneauHoraire
    form_class = CreneauHoraireForm
    template_name = 'rendezvous/creneau_form.html'
    success_url = reverse_lazy('planning_docteur')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['docteur'] = self.request.user.docteur
        return kwargs

class CreneauUpdateView(LoginRequiredMixin, UpdateView):
    model = CreneauHoraire
    form_class = CreneauHoraireForm
    template_name = 'rendezvous/creneau_form.html'
    success_url = reverse_lazy('planning_docteur')

    def get_queryset(self):
        return super().get_queryset().filter(docteur=self.request.user.docteur)

class CreneauDeleteView(LoginRequiredMixin, DeleteView):
    model = CreneauHoraire
    template_name = 'rendezvous/creneau_confirm_delete.html'
    success_url = reverse_lazy('planning_docteur')

    def get_queryset(self):
        return super().get_queryset().filter(docteur=self.request.user.docteur)
