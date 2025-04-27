from django.db import models
from apps.reservations.models import Reservation


class Paiement(models.Model):
    MOYEN_CHOICES = [
        ('OM', 'Orange Money'),
        ('WAVE', 'Wave'),
        ('CB', 'Carte Bancaire'),
        ('PAYPAL', 'PayPal'),
        ('ESPECES', 'Espèces'),
    ]

    STATUT_CHOICES = [
        ('REUSSI', 'Réussi'),
        ('ECHEC', 'Échoué'),
        ('EN_ATTENTE', 'En attente'),
        ('REMBOURSE', 'Remboursé'),
    ]

    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE, related_name='paiement')
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    moyen_paiement = models.CharField(max_length=20, choices=MOYEN_CHOICES)
    date_paiement = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='EN_ATTENTE')
    reference_transaction = models.CharField(max_length=100, blank=True)
    
    def save(self, *args, **kwargs):
        # Mise à jour du statut de paiement de la réservation
        if self.statut == 'REUSSI' and not self.reservation.est_payee:
            self.reservation.est_payee = True
            self.reservation.statut = 'CONFIRME'
            self.reservation.save()
        elif self.statut == 'REMBOURSE' and self.reservation.est_payee:
            self.reservation.est_payee = False
            self.reservation.statut = 'ANNULEE'
            self.reservation.save()
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Paiement {self.id} - {self.statut} - {self.montant} FCFA"
    