from rest_framework import permissions


class OwnerOrReadOnly(permissions.BasePermission):
    """ Только автор может изменять и добавлять объекты. """

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user)
