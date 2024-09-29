from rest_framework import serializers
from .models import Person
from django.contrib.auth.models import User


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = '__all__'  # Exclude 'color' and 'country' fields from model if not needed.

    # Validate the 'name' field
    def validate_name(self, value):
        special_characters = "!@#$%^&*()_+{}:><?.,/-"
        if any(c in special_characters for c in value):
            raise serializers.ValidationError("Name should not contain any special characters.")
        return value

    # Validate the 'age' field
    def validate_age(self, value):
        if value < 18:
            raise serializers.ValidationError("Age must be greater than 18.")
        return value



class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    # Validate username
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value

    # Validate email
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def create(self, validated_data):
        # Create user object
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email']
        )
        
        # Set password and save the user
        user.set_password(validated_data['password'])
        user.save()

        return user
    


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()