from rest_framework.decorators import action, api_view, permission_classes
from rest_framework import viewsets, status, permissions, generics
from rest_framework.response import Response
from django.db.models import Q, Sum, Count
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.utils import timezone
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView  

from apps.trajets.models import Trajet
from apps.compagnies.models import CompagnieTransport, AgentCompagnie
from apps.reservations.models import Reservation
from apps.paiements.models import Paiement
from apps.users.models import User
from apps.conducteurs.models import Conducteur
from apps.vehicules.models import Vehicule


from .serializers import (
    UserSerializer,
    
    RegisterSerializer,
    ChangePasswordSerializer,
    EmailTokenObtainPairSerializer,
    CompagnieTransportSerializer,
    AgentCompagnieSerializer,
    ConducteurSerializer,
    VehiculeSerializer,
    TrajetSerializer,
    ReservationSerializer,
    PaiementSerializer
)
from .permissions import RoleBasedPermission, IsAdminUser, IsOwnerOrReadOnly, IsCompagnieAgent
from drf_spectacular.utils import extend_schema


# Vue dédiée à l'inscription, distincte du UserViewSet
class RegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED) 
class LoginAPIView(APIView):
    # permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        # Get credentials from request
        identifier = request.data.get('email')  # This can be email or phone
        password = request.data.get('password')
        
        if not identifier or not password:
            return Response(
                {'error': 'Please provide both identifier (email or phone) and password'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Try to find the user by email or phone
        user = None
        
        # Check if identifier is an email
        if '@' in identifier:
            try:
                user = User.objects.get(email=identifier)
            except User.DoesNotExist:
                pass
        # Check if identifier is a phone number
        else:
            try:
                user = User.objects.get(telephone=identifier)  # Assuming you have a phone field
            except User.DoesNotExist:
                pass
        
        # If user is not found or password doesn't match
        # if not user or not user.check_password(password):
        #     return Response(
        #         {'error': 'Invalid credentials'},
        #         status=status.HTTP_401_UNAUTHORIZED
        #     )
        
        # If authentication is successful, generate tokens
        if user.is_active:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': 'Account is disabled'},
                status=status.HTTP_401_UNAUTHORIZED
            )
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [permissions.IsAuthenticated]
    
    # def get_permissions(self):
    #     if self.action == 'create':
    #         permission_classes = [permissions.AllowAny]
    #     elif self.action in ['update', 'partial_update', 'destroy']:
    #         permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    #     else:
    #         permission_classes = [permissions.IsAuthenticated]
    #     return [permission() for permission in permission_classes]
    
    @extend_schema(request=RegisterSerializer, responses={201: UserSerializer})
    @action(detail=False, methods=['post'], 
        permission_classes=[permissions.AllowAny],  # Décommentez cette ligne
        serializer_class=RegisterSerializer)
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(request=ChangePasswordSerializer, responses={200: {"message": "string"}})
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated], serializer_class=ChangePasswordSerializer)
    def change_password(self, request):
        user = request.user
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            # Vérifier l'ancien mot de passe
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({'old_password': ['Mot de passe incorrect.']}, status=status.HTTP_400_BAD_REQUEST)
            
            # Mettre à jour avec le nouveau mot de passe
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            # Générer et renvoyer de nouveaux tokens après changement du mot de passe
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Mot de passe modifié avec succès.',
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """Récupérer les données de l'utilisateur connecté"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class CompagnieTransportViewSet(viewsets.ModelViewSet):
    queryset = CompagnieTransport.objects.all()
    serializer_class = CompagnieTransportSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['get'])
    def vehicules(self, request, pk=None):
        compagnie = self.get_object()
        vehicules = Vehicule.objects.filter(compagnie=compagnie)
        serializer = VehiculeSerializer(vehicules, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def conducteurs(self, request, pk=None):
        compagnie = self.get_object()
        conducteurs = Conducteur.objects.filter(compagnie=compagnie)
        serializer = ConducteurSerializer(conducteurs, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def trajets(self, request, pk=None):
        compagnie = self.get_object()
        vehicules = Vehicule.objects.filter(compagnie=compagnie)
        trajets = Trajet.objects.filter(vehicule__in=vehicules)
        serializer = TrajetSerializer(trajets, many=True)
        return Response(serializer.data)
        
      
class AgentCompagnieViewSet(viewsets.ModelViewSet):
    queryset = AgentCompagnie.objects.all()
    serializer_class = AgentCompagnieSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsAdminUser | IsCompagnieAgent]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]


class ConducteurViewSet(viewsets.ModelViewSet):
    queryset = Conducteur.objects.all()
    serializer_class = ConducteurSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsAdminUser | IsCompagnieAgent]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['get'])
    def trajets(self, request, pk=None):
        conducteur = self.get_object()
        trajets = Trajet.objects.filter(conducteur=conducteur)
        serializer = TrajetSerializer(trajets, many=True)
        return Response(serializer.data)


class VehiculeViewSet(viewsets.ModelViewSet):
    queryset = Vehicule.objects.all()
    serializer_class = VehiculeSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsAdminUser | IsCompagnieAgent]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['get'])
    def trajets(self, request, pk=None):
        vehicule = self.get_object()
        trajets = Trajet.objects.filter(vehicule=vehicule)
        serializer = TrajetSerializer(trajets, many=True)
        return Response(serializer.data)


class TrajetViewSet(viewsets.ModelViewSet):
    queryset = Trajet.objects.all()
    serializer_class = TrajetSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsAdminUser | IsCompagnieAgent]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        queryset = Trajet.objects.all()
        
        # Filtrage par ville de départ
        ville_depart = self.request.query_params.get('ville_depart')
        if ville_depart:
            queryset = queryset.filter(ville_depart__icontains=ville_depart)
        
        # Filtrage par ville d'arrivée
        ville_arrivee = self.request.query_params.get('ville_arrivee')
        if ville_arrivee:
            queryset = queryset.filter(ville_arrivee__icontains=ville_arrivee)
        
        # Filtrage par date de départ
        date_depart = self.request.query_params.get('date_depart')
        if date_depart:
            queryset = queryset.filter(date_depart__date=date_depart)
        
        # Filtrage par places disponibles
        places_min = self.request.query_params.get('places_min')
        if places_min:
            queryset = queryset.filter(nombre_places_total__gte=int(places_min) + models.F('nombre_places_reservees'))
        
        # Filtrage par covoiturage
        covoiturage = self.request.query_params.get('covoiturage')
        if covoiturage:
            queryset = queryset.filter(covoiturage=(covoiturage.lower() == 'true'))
        
        # Filtrage par compagnie
        compagnie_id = self.request.query_params.get('compagnie_id')
        if compagnie_id:
            queryset = queryset.filter(vehicule__compagnie_id=compagnie_id)
            
        return queryset
    
    @action(detail=True, methods=['get'])
    def reservations(self, request, pk=None):
        trajet = self.get_object()
        reservations = Reservation.objects.filter(trajet=trajet)
        serializer = ReservationSerializer(reservations, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def update_position(self, request, pk=None):
        trajet = self.get_object()
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        
        if not latitude or not longitude:
            return Response({"error": "Latitude et longitude requises"}, status=status.HTTP_400_BAD_REQUEST)
        
        trajet.latitude_actuelle = latitude
        trajet.longitude_actuelle = longitude
        trajet.derniere_maj_position = timezone.now()
        trajet.save()
        
        return Response({"success": "Position mise à jour"}, status=status.HTTP_200_OK)


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly | IsAdminUser | IsCompagnieAgent]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        if self.request.user.role == 'VOYAGEUR':
            return Reservation.objects.filter(utilisateur=self.request.user)
        elif self.request.user.role == 'AGENT':
            try:
                agent = AgentCompagnie.objects.get(utilisateur=self.request.user)
                vehicules = Vehicule.objects.filter(compagnie=agent.compagnie)
                trajets = Trajet.objects.filter(vehicule__in=vehicules)
                return Reservation.objects.filter(trajet__in=trajets)
            except AgentCompagnie.DoesNotExist:
                return Reservation.objects.none()
        return Reservation.objects.all()
    
    def create(self, request, *args, **kwargs):
        # Ajouter l'utilisateur courant comme voyageur
        request.data['utilisateur'] = request.user.id
        
        # Vérifier la disponibilité des places
        trajet_id = request.data.get('trajet')
        nb_places = int(request.data.get('nb_places', 1))
        
        try:
            trajet = Trajet.objects.get(id=trajet_id)
            if trajet.places_disponibles() < nb_places:
                return Response(
                    {"error": f"Seulement {trajet.places_disponibles()} places disponibles"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Trajet.DoesNotExist:
            return Response({"error": "Trajet non trouvé"}, status=status.HTTP_404_NOT_FOUND)
        
        return super().create(request, *args, **kwargs)
    
    @action(detail=True, methods=['get'])
    def paiement(self, request, pk=None):
        reservation = self.get_object()
        try:
            paiement = Paiement.objects.get(reservation=reservation)
            serializer = PaiementSerializer(paiement)
            return Response(serializer.data)
        except Paiement.DoesNotExist:
            return Response({"error": "Aucun paiement associé"}, status=status.HTTP_404_NOT_FOUND)


class PaiementViewSet(viewsets.ModelViewSet):
    queryset = Paiement.objects.all()
    serializer_class = PaiementSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsAdminUser | IsCompagnieAgent]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        if self.request.user.role == 'VOYAGEUR':
            return Paiement.objects.filter(reservation__utilisateur=self.request.user)
        elif self.request.user.role == 'AGENT':
            try:
                agent = AgentCompagnie.objects.get(utilisateur=self.request.user)
                vehicules = Vehicule.objects.filter(compagnie=agent.compagnie)
                trajets = Trajet.objects.filter(vehicule__in=vehicules)
                reservations = Reservation.objects.filter(trajet__in=trajets)
                return Paiement.objects.filter(reservation__in=reservations)
            except AgentCompagnie.DoesNotExist:
                return Paiement.objects.none()
        return Paiement.objects.all()
    
    def create(self, request, *args, **kwargs):
        # Vérifier que la réservation existe et appartient à l'utilisateur
        reservation_id = request.data.get('reservation')
        try:
            reservation = Reservation.objects.get(id=reservation_id)
            if request.user.role == 'VOYAGEUR' and reservation.utilisateur != request.user:
                return Response(
                    {"error": "Vous n'êtes pas autorisé à payer cette réservation"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Définir le montant automatiquement
            request.data['montant'] = reservation.montant_total()
            
        except Reservation.DoesNotExist:
            return Response({"error": "Réservation non trouvée"}, status=status.HTTP_404_NOT_FOUND)
        
        return super().create(request, *args, **kwargs)

# Nouvelle vue pour l'authentification par email
class LoginView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer 

