from rest_framework import permissions


class IsObjectOwner(permissions.BasePermission):
    message = "u are not the creator of this "

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "owner_id"):
            return obj.owner_id == request.user.id

        if hasattr(obj, "user_id"):
            return obj.user_id == request.user.id

        if hasattr(obj, "channel") and hasattr(obj.channel, "owner_id"):
            return obj.channel.owner_id == request.user.id

        return False
