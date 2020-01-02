from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=128)
    password = serializers.CharField(max_length=128)
    # access_token = serializers.CharField(max_length=255, read_only=True)
    # refresh_token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        print(data)
        username = data.get('username', None)
        password = data.get('password', None)
        if username is None:
            raise serializers.ValidationError(
                    'Username is required to login'
                    )
        if password is None:
            raise serializers.ValidationError(
                    'Password is required to login'
                    )
        user = authenticate(username=username, password=password)
        if user is None:
            raise serializers.ValidationError(
                    'Username with given password doesn\'t exists'
                    )
        if not user.is_active:
            raise serializers.ValidationError(
                    'The user is deactivated.'
                    )
        token = RefreshToken.for_user(user)

        return {
                "meta":{
                    "username": username,
                    "verified": user.account_verified()
                    },
                "data":{
                    "refresh" : str(token),
                    "access" : str(token.access_token)
                }
            }


