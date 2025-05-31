from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """только владелец может редактировать, остальные — read-only."""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user


class IsNotSubscribed(permissions.BasePermission):
    """Запрещает подписаться на самого себя."""
    def has_permission(self, request, view):
        if view.action == 'subscribe':
            author_id = view.kwargs.get('pk')
            return request.user.id != int(author_id)
        return True


class IsSubscribedOrReadOnly(permissions.BasePermission):
    """Разрешает удалять подписку только если она существует."""
    def has_permission(self, request, view):
        if view.action == 'subscribe' and request.method == 'DELETE':
            author_id = view.kwargs.get('pk')
            return request.user.subscriptions.filter(id=author_id).exists()
        return True
