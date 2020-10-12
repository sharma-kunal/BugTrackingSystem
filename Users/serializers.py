from rest_framework import serializers
from .models import Projects, Tickets
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=200)
    password = serializers.CharField(max_length=100, write_only=True)
    email = serializers.EmailField(max_length=255)
    first_name = serializers.CharField(max_length=255)
    last_name = serializers.CharField(max_length=255)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']

    def validate(self, attrs):
        if User.objects.filter(email=attrs['email']).exists():
            print("email exists")
            raise serializers.ValidationError({'email', 'Email is already in use'})
        return super().validate(attrs)

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        Token.objects.create(user=user)
        return user


class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Projects
        fields = ['id', 'name', 'description', 'ticket_form_key']


class TicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tickets
        fields = '__all__'
