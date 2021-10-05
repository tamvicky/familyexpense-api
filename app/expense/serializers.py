from rest_framework import serializers

from core.models import Category


class CateogrySerializer(serializers.ModelSerializer):
    """Serializer for tag objects"""

    class Meta:
        model = Category
        fields = ('id', 'name')
        read_only_fields = ('id', )
