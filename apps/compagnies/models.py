from django.db import models
from apps.users.models import User

class CompagnieTransport(models.Model):
    nom = models.CharField(max_length=100)
    adresse = models.CharField(max_length=255)
    telephone = models.CharField(max_length=20)
    email = models.EmailField()
    logo = models.ImageField(upload_to='compagnies/logos/', blank=True, null=True)
    description = models.TextField(blank=True)
    date_creation = models.DateField(auto_now_add=True)
    statut = models.BooleanField(default=True)
    responsable = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, related_name='compagnie_responsable')
    
    def __str__(self):
        return self.nom

class AgentCompagnie(models.Model):
    utilisateur = models.OneToOneField(User, on_delete=models.CASCADE)
    compagnie = models.ForeignKey(CompagnieTransport, on_delete=models.CASCADE, related_name='agents')
    localisation = models.CharField(max_length=255)
    date_embauche = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.utilisateur.prenom} {self.utilisateur.nom} - {self.compagnie.nom}"
