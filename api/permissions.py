from rest_framework import permissions
from apps.compagnies.models import AgentCompagnie

class IsSuperUser(permissions.BasePermission):
    """
    Permission pour les administrateurs uniquement
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


class RoleBasedPermission(permissions.BasePermission):
    """
    Permission basée sur le rôle utilisateur et le type de ressource
    """
    def has_permission(self, request, view):
        # Les administrateurs ont accès à tout
        if request.user.is_superuser or request.user.user_type == 'admin':
            return True
        
        # Pour les étudiants
        if view.basename == 'student':
            if request.user.user_type in ['surveillant', 'director', 'secretary']:
                return True
            if request.user.user_type == 'cashier' and request.method in ['GET']:
                return True
        
        # Pour les paiements
        if view.basename == 'payment':
            if request.user.user_type == 'cashier':
                return request.method in ['GET', 'POST', 'PUT', 'PATCH']
            if request.user.user_type in ['director', 'secretary']:
                return request.method in ['GET']
        
        # Pour les classes
        if view.basename == 'class':
            if request.user.user_type in ['surveillant', 'director', 'secretary']:
                return True
            if request.user.user_type == 'cashier' and request.method in ['GET']:
                return True
        
        # Pour les écoles
        if view.basename == 'school':
            if request.user.user_type in ['director', 'secretary']:
                return True
            if request.user.user_type in ['surveillant', 'cashier'] and request.method in ['GET']:
                return True
        
        return False

class IsAdminUser(permissions.BasePermission):
    """
    Permission pour limiter l'accès aux utilisateurs admin.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'ADMIN'

class IsCompagnieAgent(permissions.BasePermission):
    """
    Permission pour limiter l'accès aux agents de compagnie.
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated and request.user.role == 'AGENT'):
            return False
        
        # Vérifier si l'utilisateur est associé à une compagnie
        try:
            AgentCompagnie.objects.get(utilisateur=request.user)
            return True
        except AgentCompagnie.DoesNotExist:
            return False

class IsConducteur(permissions.BasePermission):
    """
    Permission pour limiter l'accès aux conducteurs.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'CONDUCTEUR'

class IsVoyageur(permissions.BasePermission):
    """
    Permission pour limiter l'accès aux voyageurs.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'VOYAGEUR'

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission pour permettre aux propriétaires d'objets de les modifier.
    """
    def has_object_permission(self, request, view, obj):
        # Les requêtes en lecture sont autorisées pour tous
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # L'utilisateur doit être le propriétaire
        if hasattr(obj, 'utilisateur'):
            return obj.utilisateur == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        return False

class IsCompagnieOwnerOrAdmin(permissions.BasePermission):
    """
    Permission pour permettre aux responsables de compagnie ou aux admins de modifier.
    """
    def has_object_permission(self, request, view, obj):
        # Les requêtes en lecture sont autorisées pour tous les utilisateurs authentifiés
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Les admins ont tous les droits
        if request.user.role == 'ADMIN':
            return True
        
        # Pour les objets liés à une compagnie
        if hasattr(obj, 'compagnie') and obj.compagnie.responsable == request.user:
            return True
        
        # Pour les compagnies elles-mêmes
        if hasattr(obj, 'responsable') and obj.responsable == request.user:
            return True
        
        return False 