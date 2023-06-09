from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            **extra_fields
        )
        user.set_password(password)

        user.save()
        return user
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser has to have is_staff being True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser has to have is_superuser being True")

        return self.create_user(email=email, password=password, **extra_fields)
    

class Tag(models.Model):
    name = models.CharField(max_length=20)

class Note(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, null=True, related_name="user_notes")
    title = models.CharField(max_length=40)
    body = models.CharField(max_length= 120)
    tags = models.ManyToManyField(Tag, blank=True, related_name="note")
    created = models.DateTimeField(auto_now_add=True)
    public = models.BooleanField(default=False)

class User(AbstractUser):
    email = models.CharField(max_length=80,unique=True)
    username = models.CharField(max_length=45)
    date_of_birth=models.DateField(null=True)

    objects=CustomUserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username
    
