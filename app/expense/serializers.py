from rest_framework import serializers

from core.models import Category, ExpenseRecord
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


class ExpenseRecordDetailsSerializer(serializers.ModelSerializer):
    """Serializer for expense record details"""
    class Meta:
        model = ExpenseRecord
        fields = (
            'id', 'user', 'family', 'category', 'date', 'amount', 'notes'
            )
        read_only_fields = ('id', )


class ExpenseRecordListSerializer(serializers.ModelSerializer):
    """Serializer for expense record list"""
    user = UserSerializer()
    family = FamilySerializer()
    category = CateogryListSerializer()

    class Meta:
        model = ExpenseRecord
        fields = (
            'id', 'user', 'family', 'category', 'date', 'amount', 'notes'
            )
        read_only_fields = ('id', )
