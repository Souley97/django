from django.db import models
from apps.users.models import User
from apps.compagnies.models import CompagnieTransport

class Conducteur(models.Model):
    STATUT_CHOICES = [
        ('DISPONIBLE', 'Disponible'),
        ('EN_SERVICE', 'En service'),
        ('EN_PAUSE', 'En pause'),
        ('INDISPONIBLE', 'Indisponible'),
    ]
    
    utilisateur = models.OneToOneField(User, on_delete=models.CASCADE)
    numero_permis = models.CharField(max_length=100, unique=True)
    date_emission_permis = models.DateField()
    date_expiration_permis = models.DateField()
    disponibilite = models.BooleanField(default=True)
    statut = models.CharField(max_length=50, choices=STATUT_CHOICES, default='DISPONIBLE')
    localisation_actuelle = models.CharField(max_length=255, blank=True)
    compagnie = models.ForeignKey(CompagnieTransport, on_delete=models.CASCADE, related_name='conducteurs')
    experience = models.PositiveIntegerField(default=0, help_text="Expérience en années")
    
    def __str__(self):
        return f"{self.utilisateur.prenom} {self.utilisateur.nom} - {self.numero_permis}"
