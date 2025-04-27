from django.db import models
from apps.compagnies.models import CompagnieTransport
from apps.conducteurs.models import Conducteur

class Vehicule(models.Model):
    TYPE_CHOICES = [
        ('BUS', 'Bus'),
        ('MINIBUS', 'Minibus'),
        ('VAN', 'Van'),
        ('VOITURE', 'Voiture'),
    ]
    
    immatriculation = models.CharField(max_length=50, unique=True)
    capacite = models.PositiveIntegerField()
    modele = models.CharField(max_length=100)
    marque = models.CharField(max_length=100)
    annee_fabrication = models.PositiveIntegerField()
    type_vehicule = models.CharField(max_length=20, choices=TYPE_CHOICES)
    compagnie = models.ForeignKey(CompagnieTransport, on_delete=models.CASCADE, related_name='vehicules')
    conducteur = models.ForeignKey(Conducteur, on_delete=models.SET_NULL, null=True, blank=True, related_name='vehicules')
    localisation_actuelle = models.CharField(max_length=255, blank=True)
    est_actif = models.BooleanField(default=True)
    date_dernier_entretien = models.DateField(null=True, blank=True)
    photo = models.ImageField(upload_to='vehicules/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.marque} {self.modele} - {self.immatriculation}"

    