from rest_framework import serializers
from .models import *

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = '__all__'
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=50)
    body = serializers.CharField()
    created = serializers.DateTimeField(read_only=True)