from rest_framework.validators import ValidationError
from rest_framework.serializers import ModelSerializer, CharField, HyperlinkedRelatedField
from base.models import Note, Tag, User

class NoteSerializer(ModelSerializer):
    class Meta:
        model = Note
        fields = '__all__'

class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

class SignUpSerializer(ModelSerializer):
    email = CharField(max_length=80)
    username = CharField(max_length=80)

    #password is only for editing
    password = CharField(min_length=8, write_only=True)
    class Meta:
        model = User
        fields = ['email', 'username', 'password']

    def validate(self, attrs):
        email_exists=User.objects.filter(email=attrs['email']).exists()
        if email_exists:
            raise ValidationError("Email has already been used")
        return super().validate(attrs)

    #overwrite the create method with custom method to hide password chars in admin view
    def create(self, validated_data):
        password = validated_data.pop("password")

        user = super().create(validated_data)
        #actually update and hash password
        user.set_password(password)
        user.save()
        return user

class LogInSerializer(ModelSerializer):
    email = CharField(max_length=80)
    password = CharField(min_length=8, write_only=True)
    class Meta:
        model = User
        fields = ['email', 'password']
    
class CurrentUserNotesSerializer(ModelSerializer):
    posts = HyperlinkedRelatedField(
        many=True, view_name="post_detail", queryset=User.objects.all()
    )

    class Meta:
        model = User
        fields = ["id", "username", "email", "posts"]