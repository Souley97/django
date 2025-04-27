from django.db import models
from django.conf import settings
from apps.trajets.models import Trajet
from apps.users.models import User

class Reservation(models.Model):
    STATUT_CHOICES = [
        ('CONFIRME', 'Confirmée'),
        ('ANNULEE', 'Annulée'),
        ('ATTENTE', 'En attente'),
        ('TERMINEE', 'Terminée'),
    ]

    trajet = models.ForeignKey(Trajet, on_delete=models.CASCADE, related_name='reservations')
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    date_reservation = models.DateTimeField(auto_now_add=True)
    nb_places = models.PositiveIntegerField(default=1)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='ATTENTE')
    code_reservation = models.CharField(max_length=20, unique=True)
    est_payee = models.BooleanField(default=False)
    informations_passagers = models.TextField(blank=True, help_text="Informations sur les passagers supplémentaires")
    
    def montant_total(self):
        return self.trajet.prix_par_place * self.nb_places
    
    def save(self, *args, **kwargs):
        # Générer un code de réservation s'il n'existe pas déjà
        if not self.code_reservation:
            import uuid
            self.code_reservation = str(uuid.uuid4()).split('-')[0].upper()
        
        # Mettre à jour le nombre de places réservées sur le trajet
        is_new = self.pk is None
        if is_new and self.statut == 'CONFIRME':
            self.trajet.nombre_places_reservees += self.nb_places
            self.trajet.save()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Réservation {self.code_reservation} - {self.utilisateur.prenom} {self.utilisateur.nom}"
