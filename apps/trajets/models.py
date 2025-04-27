from django.db import models
from apps.vehicules.models import Vehicule
from apps.conducteurs.models import Conducteur

class Trajet(models.Model):
    STATUT_CHOICES = [
        ('PROGRAMME', 'Programmé'),
        ('EN_COURS', 'En cours'),
        ('TERMINE', 'Terminé'),
        ('ANNULE', 'Annulé'),
    ]
    
    vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE, related_name='trajets')
    conducteur = models.ForeignKey(Conducteur, on_delete=models.CASCADE, related_name='trajets')
    ville_depart = models.CharField(max_length=100)
    ville_arrivee = models.CharField(max_length=100)
    lieu_depart = models.CharField(max_length=255)
    lieu_arrivee = models.CharField(max_length=255)
    date_depart = models.DateTimeField()
    date_arrivee_estimee = models.DateTimeField()
    date_arrivee_reelle = models.DateTimeField(null=True, blank=True)
    nombre_places_total = models.PositiveIntegerField()
    nombre_places_reservees = models.PositiveIntegerField(default=0)
    prix_par_place = models.DecimalField(max_digits=10, decimal_places=2)
    covoiturage = models.BooleanField(default=False)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='PROGRAMME')
    latitude_actuelle = models.FloatField(null=True, blank=True)
    longitude_actuelle = models.FloatField(null=True, blank=True)
    derniere_maj_position = models.DateTimeField(null=True, blank=True)
    
    def places_disponibles(self):
        return self.nombre_places_total - self.nombre_places_reservees
    
    def est_complet(self):
        return self.nombre_places_reservees >= self.nombre_places_total
    
    def __str__(self):
        return f"{self.ville_depart} → {self.ville_arrivee} ({self.date_depart.strftime('%d/%m/%Y %H:%M')})"
