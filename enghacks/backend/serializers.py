from django.contrib.auth import get_user_model
from rest_framework import serializers
from backend.models import UserHealthInformation

User = get_user_model()
class UserLoginSerializer(serializers.HyperlinkedModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('username','first_name', 'last_name', 'phone', 'password')

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user_health_information = UserHealthInformation.objects.create(
            user=user
        )
        return user