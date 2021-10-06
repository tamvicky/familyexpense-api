from rest_framework import viewsets, authentication, permissions
from django.db.models import Q

from core.models import Category, UserProfile, ExpenseRecord
from expense import serializers


class CategoryViewSet(viewsets.ModelViewSet):
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
        if self.request.method == 'GET':
            return serializers.CateogryListSerializer
        else:
            return serializers.CateogryCreateSerializer

    def perform_create(self, serializer):
        """Create a new category"""
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """Update category"""
        serializer.save()


class RecordViewSet(viewsets.ModelViewSet):
    """Manage expense record in the databases"""
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = ExpenseRecord.objects.all()

    def get_queryset(self):
        """
        Retrieve the expense records for the authenticated user
        """
        type = self.request.query_params.get('type')
        queryset = self.queryset
        if type == 'personal':
            queryset = queryset.filter(user=self.request.user)\
                        .filter(family__isnull=True)
        elif type == 'family':
            userprofile = UserProfile.objects.get(user=self.request.user)
            queryset = queryset.filter(family=userprofile.family)
        else:
            queryset = queryset.filter(user=self.request.user)

        return queryset.order_by('-date', '-id')

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.ExpenseRecordListSerializer
        else:
            return serializers.ExpenseRecordDetailsSerializer
