from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerProfileOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.user == request.user


class IsUserPatient(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'Patient'


class IsUserMedic(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'Doctor'


class IsUserAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'Admin'
