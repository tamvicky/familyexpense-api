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


class CateogryBasicSerializer(serializers.ModelSerializer):
    """Serializer for basic category objects"""
    class Meta:
        model = Category
        fields = ('id', 'name')
        read_only_fields = ('id', )


class ExpenseRecordDetailsSerializer(serializers.ModelSerializer):
    """Serializer for expense record details"""
    class Meta:
        model = ExpenseRecord
        fields = (
            'id', 'user', 'family', 'category', 'date', 'amount', 'notes', 'image'
            )
        read_only_fields = ('id', )


class ExpenseRecordListSerializer(serializers.ModelSerializer):
    """Serializer for expense record list"""
    user = UserSerializer()
    family = FamilySerializer()
    category = CateogryBasicSerializer()

    class Meta:
        model = ExpenseRecord
        fields = (
            'id', 'user', 'family', 'category', 'date', 'amount', 'notes', 'image'
            )
        read_only_fields = ('id', )


class RecordImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to record"""

    class Meta:
        model = ExpenseRecord
        fields = ('id', 'image')
        read_only_fields = ('id',)


class ExpenseRecordSummarySerializer(serializers.ModelSerializer):
    """Serializer for record summary"""
    total_amount = serializers.DecimalField(max_digits=6, decimal_places=2)
    cat_id = serializers.SerializerMethodField('get_cat_id')
    cat_name = serializers.SerializerMethodField('get_cat_name')

    class Meta:
        model = ExpenseRecord
        fields = ('id', 'cat_id', 'cat_name', 'total_amount')

    def get_cat_name(self, obj):
        return obj.get('category__name')

    def get_cat_id(self, obj):
        return obj.get('category__id')
