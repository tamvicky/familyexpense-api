from rest_framework import viewsets, mixins, authentication, permissions
from django.db.models import Q

from core.models import Category, UserProfile
from expense import serializers


class CategoryViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    """Manage category in the databases"""
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Category.objects.all()
    serializer_class = serializers.CateogrySerializer

    def get_queryset(self):
        """
        Return categories which is public or belongs to authenticated
        user & family
        """
        userprofile = UserProfile.objects.get(user=self.request.user)
        return self.queryset.filter(Q(isPublic=True) |
                                    Q(user=self.request.user) |
                                    Q(family=userprofile.family))
