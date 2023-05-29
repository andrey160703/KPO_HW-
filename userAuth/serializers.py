from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import User

import hashlib


def hash_password(password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return hashed_password


class UserSerializer(serializers.Serializer):
    class Meta:
        model = User
        fields = '__all__'

    username = serializers.CharField(max_length=50, validators=[UniqueValidator(queryset=User.objects.all())])
    email = serializers.EmailField(validators=[UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(max_length=128, write_only=True)
    role = serializers.CharField(max_length=128, write_only=True)

    def validate_password(self, value):
        return hash_password(value)

    def create(self, validated_data):
        validated_data['password_hash'] = validated_data.pop('password')
        return User.objects.create(**validated_data)
