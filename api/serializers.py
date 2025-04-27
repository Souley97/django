from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.users.models import User
from apps.compagnies.models import CompagnieTransport, AgentCompagnie
from apps.conducteurs.models import Conducteur
from apps.vehicules.models import Vehicule
from apps.trajets.models import Trajet
from apps.reservations.models import Reservation
from apps.paiements.models import Paiement

# User Serializers
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id',  'nom', 'prenom', 'sexy', 'telephone', 
                 'email', 'photo_profile', 'statut', 'role']
        read_only_fields = ['id']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = [ 'nom', 'prenom', 'sexy', 'telephone', 
                 'email', 'password', 'password2', 'role']
        
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Les mots de passe ne correspondent pas."})
        
        try:
            validate_password(attrs['password'])
        except ValidationError as e:
            raise serializers.ValidationError({"password": list(e)})
        
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

# CompagnieTransport Serializers
class CompagnieTransportSerializer(serializers.ModelSerializer):
    responsable_nom = serializers.CharField(source='responsable.get_full_name', read_only=True)
    
    class Meta:
        model = CompagnieTransport
        fields = '__all__'

class AgentCompagnieSerializer(serializers.ModelSerializer):
    utilisateur_details = UserSerializer(source='utilisateur', read_only=True)
    compagnie_nom = serializers.CharField(source='compagnie.nom', read_only=True)
    
    class Meta:
        model = AgentCompagnie
        fields = '__all__'

# Conducteur Serializers
class ConducteurSerializer(serializers.ModelSerializer):
    utilisateur_details = UserSerializer(source='utilisateur', read_only=True)
    compagnie_nom = serializers.CharField(source='compagnie.nom', read_only=True)
    
    class Meta:
        model = Conducteur
        fields = '__all__'

# Vehicule Serializers
class VehiculeSerializer(serializers.ModelSerializer):
    compagnie_nom = serializers.CharField(source='compagnie.nom', read_only=True)
    conducteur_nom = serializers.SerializerMethodField()
    
    class Meta:
        model = Vehicule
        fields = '__all__'
    
    def get_conducteur_nom(self, obj):
        if obj.conducteur:
            return f"{obj.conducteur.utilisateur.prenom} {obj.conducteur.utilisateur.nom}"
        return None

# Trajet Serializers
class TrajetSerializer(serializers.ModelSerializer):
    vehicule_details = VehiculeSerializer(source='vehicule', read_only=True)
    conducteur_details = ConducteurSerializer(source='conducteur', read_only=True)
    places_disponibles = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Trajet
        fields = '__all__'

# Reservation Serializers
class ReservationSerializer(serializers.ModelSerializer):
    trajet_details = TrajetSerializer(source='trajet', read_only=True)
    utilisateur_details = UserSerializer(source='utilisateur', read_only=True)
    montant_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Reservation
        fields = '__all__'
        read_only_fields = ['code_reservation', 'montant_total']

# Paiement Serializers
class PaiementSerializer(serializers.ModelSerializer):
    reservation_details = ReservationSerializer(source='reservation', read_only=True)
    
    class Meta:
        model = Paiement
        fields = '__all__'

# Email Token Serializer
class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = User.USERNAME_FIELD
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['email'] = serializers.CharField(required=True)
        self.fields['password'] = serializers.CharField(required=True, style={'input_type': 'password'})
        
        # Supprimer le champ username s'il existe
        # if 'username' in self.fields:
        #     del self.fields['username']
    
    def validate(self, attrs):
        # Récupérer l'utilisateur par email
        email = attrs.get('email')
        password = attrs.get('password')
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({'email': 'Aucun utilisateur trouvé avec cet email.'})
        
        # Vérifier mot de passe avec username
        attrs['password'] = user.password
        
        # Supprimer email pour éviter les conflits
        del attrs['email']
        
        # Utiliser la validation de la classe parent
        return super().validate(attrs) 

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, style={'input_type': 'password'})
    new_password = serializers.CharField(required=True, style={'input_type': 'password'})
    new_password2 = serializers.CharField(required=True, style={'input_type': 'password'})
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "Les nouveaux mots de passe ne correspondent pas."})
        
        try:
            validate_password(attrs['new_password'])
        except ValidationError as e:
            raise serializers.ValidationError({"new_password": list(e)})
        
        return attrs