from rest_framework import serializers

from core.models import Category
from user.serializers import UserSerializer, FamilySerializer


class CateogryCreateSerializer(serializers.ModelSerializer):
    """Serializer for cateogry objects create"""

    class Meta:
        model = Category
        fields = ('id', 'name', 'isPublic', 'family')
        read_only_fields = ('id', )


class CateogryListSerializer(serializers.ModelSerializer):
    """Serializer for category objects listing"""
    user = UserSerializer()
    family = FamilySerializer()

    class Meta:
        model = Category
        fields = ('id', 'name', 'isPublic', 'user', 'family')
        read_only_fields = ('id', )
