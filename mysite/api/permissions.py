from rest_framework.permissions import BasePermission


class IsAdminOrReadOnly(BasePermission):
    
    def has_permission(self, request, view):
        return request.method in ['GET', 'HEAD'] or request.user.is_superuser
    
class ReturnFromAdmin(BasePermission):
    
    def has_permission(self, request, view):
        if view.action in ['approve', 'decline']:
            return request.user.is_superuser
        return request.user.is_authenticated