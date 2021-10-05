from rest_framework import viewsets, mixins, authentication, permissions
from django.db.models import Q

from core.models import Category, UserProfile
from expense import serializers


class CategoryViewSet(viewsets.GenericViewSet, mixins.ListModelMixin,
                      mixins.CreateModelMixin):
    """Manage category in the databases"""
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Category.objects.all()

    def get_queryset(self):
        """
        Return categories which is public or belongs to authenticated
        user & family
        """
        userprofile = UserProfile.objects.get(user=self.request.user)
        return self.queryset.filter(Q(isPublic=True) |
                                    Q(user=self.request.user) |
                                    Q(family=userprofile.family))

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.CateogryCreateSerializer
        else:
            return serializers.CateogryListSerializer

    def perform_create(self, serializer):
        """Create a new category"""
        serializer.save(user=self.request.user)
