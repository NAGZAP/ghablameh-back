from rest_framework import serializers
from core.models import ForgetPasswordVerification, User,EmailVerification
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password


class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ['first_name','last_name','username','email','phone_number','date_joined']


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=127)
    password = serializers.CharField(max_length=127)
    
    
class SignUpSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
            required=True,
            validators=[UniqueValidator(queryset=User.objects.all())]
            )

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name','phone_number')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        user = User.objects.create(
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
    
    
    
class EmailVerificationSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=5)
    email = serializers.EmailField()
    
    def validate(self, attrs):
        user = User.objects.get(email=attrs['email'])
        verification = EmailVerification.objects.get(user=user)
        if not user or not verification:
            raise serializers.ValidationError({"email":"ایمیل وارد شده معتبر نیست"})
        if verification.is_expired():
            raise serializers.ValidationError({"code":"کد اعتبار سنجی منقضی شده است"})
        if not verification.is_valid(attrs['code']):
            raise serializers.ValidationError({"code":"کد اعتبار سنجی وارد شده صحیح نیست"})
        return super().validate(attrs)
    
    
    
    

class ResendEmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def validate(self, attrs):
        user = User.objects.get(email=attrs['email'])
        if not user:
            raise serializers.ValidationError({"email":"ایمیل وارد شده معتبر نیست"})
        if not EmailVerification.objects.filter(user=user).exists():
            raise serializers.ValidationError({"email":"ایمیل وارد شده معتبر نیست"})
        if user.is_verified:
            raise serializers.ValidationError({"email":"ایمیل وارد شده قبلا تایید شده است"})
        return super().validate(attrs)
    
    
class ForgetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def validate(self, attrs):
        user = User.objects.get(email=attrs['email'])
        if not user:
            raise serializers.ValidationError({"email":"ایمیل وارد شده معتبر نیست"})
        return super().validate(attrs)
    
class ForgetPasswordVerificationSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=5)
    email = serializers.EmailField()
    new_password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    new_password2 = serializers.CharField(write_only=True, required=True)
    
    def validate(self, attrs):
        user = User.objects.get(email=attrs['email'])
        verification = ForgetPasswordVerification.objects.get(user=user)
        if not user or not verification:
            raise serializers.ValidationError({"email":"ایمیل وارد شده معتبر نیست"})
        if verification.is_expired():
            raise serializers.ValidationError({"code":"کد اعتبار سنجی منقضی شده است"})
        if not verification.is_valid(attrs['code']):
            raise serializers.ValidationError({"code":"کد اعتبار سنجی وارد شده صحیح نیست"})
        return super().validate(attrs)
    
    def save(self, **kwargs):
        user = User.objects.get(email=self.validated_data['email'])
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user