from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from .views import (
    UserViewSet,
    CompagnieTransportViewSet,
    AgentCompagnieViewSet,
    ConducteurViewSet,
    VehiculeViewSet,
    TrajetViewSet,
    ReservationViewSet,
    PaiementViewSet,
    LoginView,
    RegisterAPIView,
    LoginAPIView
)

# Création du routeur
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'compagnies', CompagnieTransportViewSet)
router.register(r'agents', AgentCompagnieViewSet)
router.register(r'conducteurs', ConducteurViewSet)
router.register(r'vehicules', VehiculeViewSet)
router.register(r'trajets', TrajetViewSet)
router.register(r'reservations', ReservationViewSet)
router.register(r'paiements', PaiementViewSet)

urlpatterns = [
    # Authentification JWT
    # path('login/', LoginView.as_view(), name='login'),
    path('login/', LoginAPIView.as_view(), name='login'),

    # path('token/', LoginView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterAPIView.as_view(), name='register'),
    # API REST
    path('', include(router.urls)),
] 