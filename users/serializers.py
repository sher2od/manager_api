from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role']
        read_only_fields = ['id', 'role']

    def validate_email(self, value):
        if value:
            user = self.instance
            qs = User.objects.filter(email__iexact=value)
            if user:
                qs = qs.exclude(pk=user.pk)
            if qs.exists():
                raise serializers.ValidationError("Bu email boshqa foydalanuvchi tomonidan ishlatilmoqda.")
        return value


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only = True,
        required = True,
        style = {'input_type':'password'},
        help_text="Parol kamida 8 ta belgidan iborat bo'lishi kerak"
    )
    class Meta:
        model = User

        fields = ['id','username','email','password','first_name','last_name']

        read_only_fields = ['id']
    
    def validate_password(self,value):
        validate_password(value)
        return value

    
    def validate_email(self,value):
        if value and User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Bu email oldin ro'xatdan otgan")
        return value

    
    def create(self,validated_data):

        password = validated_data.pop('password')


        user = User(**validated_data)
        user.role = User.Role.EMPLOYEE
        user.set_password(password)
        user.save()
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self,attrs):
        data = super().validate(attrs)
        data['username'] = self.user.username
        data['role'] = self.user.role
        return data















































