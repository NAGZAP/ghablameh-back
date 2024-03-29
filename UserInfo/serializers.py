from rest_framework import serializers
from UserInfo.models import User
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password


class GetSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=127)
    
class UpdateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
            required=True,
            validators=[UniqueValidator(queryset=User.objects.all())]
            )

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name','phone_number','gender','birthdate')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def update(self, validated_data):
        user = User.objects.update(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone_number=validated_data['phone_number'],
            gender=validated_data['gender'],
            birthdate=validated_data['birthdate']
        )
        
        user.set_password(validated_data['password'])
        user.save()

        return user