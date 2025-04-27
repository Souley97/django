from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# ===============================
# Custom User Manager & Model
# ===============================

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'email est requis")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser):
    SEXE_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
    ]

    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('AGENT', 'AgentCompagnie'),
        ('VOYAGEUR', 'Voyageur'),
        ('CONDUCTEUR', 'Conducteur'),
    ]

    matricule = models.CharField(max_length=100, unique=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    sexy = models.CharField(max_length=1, choices=SEXE_CHOICES)
    telephone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    photo_profile = models.ImageField(upload_to='profiles/', blank=True, null=True)
    statut = models.BooleanField(default=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['matricule', 'nom', 'prenom']

    objects = UserManager()

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.role})"