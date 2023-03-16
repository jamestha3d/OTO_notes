from rest_framework.response import Response
from django.shortcuts import redirect
from django.contrib.auth import authenticate
#ensure user is authenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from .permissions import ReadOnly, AuthorOrReadOnly

#import base models and serializers
from base.models import Note, Tag
from .serializers import NoteSerializer, SignUpSerializer, LogInSerializer

from rest_framework import generics, mixins, status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from .tokens import create_jwt_pair_for_user
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.core.exceptions import ObjectDoesNotExist

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        #add fields to be encoded in the token
        token['username'] = user.username
        # ...

        return token
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

@api_view(['GET'])
def index(request):
    api_urls = {
        'Get All Notes': '/notes/',
        'Add Notes': '/notes/add/'
    }
    return Response(api_urls)



""" token = openapi.Parameter('token', openapi.IN_FORM, type=openapi.TYPE_STRING, required=True)
something = openapi.Parameter('something', openapi.IN_FORM, type=openapi.TYPE_INTEGER, required=False)
@swagger_auto_schema(
    method="post",
    manual_parameters=[token, something],
    operation_id="/v2/token_api"
)
@api_view(['POST'])
 """


@swagger_auto_schema(
    method='get',
    operation_summary="List user notes",
    operation_description="This returns all notes for the current user"
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getNotes(request):
    #note = {'title': 'note1', 'body': 'some text', 'tags': 'this is some tags'}
    user = request.user
    notes = user.user_notes.all()
    serializer = NoteSerializer(notes, many=True)
    return Response(serializer.data)

@swagger_auto_schema(
    method='get',
    operation_summary="get note",
    operation_description="This returns details for given note"
)
@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def getNote(request, pk):
    user = request.user
    note = Note.objects.get(id=pk)
    if note.public or note.user == request.user:
        serializer = NoteSerializer(note)
        return Response(serializer.data)
    else:
        response = {
            "message": "You do not have the permission to view this Note"
        }
        return Response(data=response,status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='get',
    operation_summary="List all public notes",
    operation_description="This returns all public notes"
)
@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def getPublicNotes(request):
    #note = {'title': 'note1', 'body': 'some text', 'tags': 'this is some tags'}
    
    notes = Note.objects.all().filter(public = True)
    serializer = NoteSerializer(notes, many=True)
    return Response(serializer.data)

@swagger_auto_schema(
    method='post',
    operation_summary="Add note",
    operation_description="This allows current user to create note"
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addNote(request):
    data = request.data
    title = data["title"]
    body = data["body"]
    post_tag = data["tag"]
    public = data.get("public")
    user = request.user

    tag = Tag.objects.filter(name=post_tag)
    if not tag:
        tag = Tag(name=post_tag)
        tag.save()
    else:
        tag = tag[0]
    #error check
    note = Note(title=title, body=body, user=user)
    note.save()
    note.tags.add(tag)

    id = note.id
    
    response = {
        "message": "note added successfully",
        "title": title,
        "body": body,
        "tag": post_tag,
        "id": id
    }
    return Response(data=response, status=status.HTTP_201_CREATED)

@swagger_auto_schema(
    method='delete',
    operation_summary="Delete note",
    operation_description="This allows current user to delete note"
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteNote(request, pk):
    user = request.user
    note = Note.objects.get(id=pk)
    if note.user == user:
        note.delete()
        response = {
            "message": "note deleted successfully"
        
        }
        return Response(data=response, status=status.HTTP_200_OK)
    else:
        response = {
            "message": "You do not have authority to delete this note"
        }
        return Response(data=response, status=status.HTTP_401_UNAUTHORIZED)

@swagger_auto_schema(
    method='post',
    operation_summary="Update note",
    operation_description="This allows current user to update note"
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def updateNote(request, pk):
    #request object should already contain note information
    note = Note.objects.get(id=pk)
    data = request.data
    user = request.user
    if note.user == request.user:
        if data.get('title'):
            note.title = data.get('title')
        if data.get('body'):
            note.body = data.get('body')
        if data.get('public'):
            note.public = data.get('public') 

        #deal with tags later
        #note.tags.add(data.tag)
        note.save()
        serializer = NoteSerializer(note)        
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    else:
        response = {
            "message": "You do not have authority to delete this note"
        }
        return Response(data=response, status=status.HTTP_401_UNAUTHORIZED)

@swagger_auto_schema(
    method='get',
    operation_summary="Filter notes",
    operation_description="Filter notes by given tag"
)
@api_view(['GET'])
def filterNotes(request, pk):
    """filter notes by tag"""
    try:
        filter_tag = Tag.objects.get(name=pk)
    except ObjectDoesNotExist:
        response = {
            "message": "Invalid Tag"
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    user = request.user
    notes = user.user_notes.filter(tags = filter_tag)
    if notes:
        serializer = NoteSerializer(notes, many=True)
        return Response(serializer.data)
    else:
        response = {
            "message": "Invalid Tag"
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)
    
@swagger_auto_schema(
    method='get',
    operation_summary="Search notes with keyword",
    operation_description="Find notes that contain certain keyword"
)
@api_view(['GET'])
def search(request, keyword):
    #check if field contains
    notes = Note.objects.all().filter(body__icontains=keyword)
    if notes:
        serializer = NoteSerializer(notes, many=True)
        return Response(serializer.data)
    else:
        response = {
            "message": "No notes found with keyword"
        }
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)
    pass


class SignUpView(generics.GenericAPIView):
    serializer_class = SignUpSerializer
    permission_classes = []
    @swagger_auto_schema(
        operation_summary="Create User",
        operation_description="Sign up to create a user")
    def post(self, request:Request):
        data = request.data

        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save()

            response={
                "message": "User Created Successfully",
                "data": serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = []
    serializer_class = LogInSerializer
    @swagger_auto_schema(
        operation_summary="Log user in with email and password",
        operation_description="Log user in with email and password"
    )
    def post(self, request: Request):
        data = request.data
        email = request.data.get("email")
        password = request.data.get("password")
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save()
            data = serializer.data
        user = authenticate(email=email, password = password)
        if user is not None:
            tokens = create_jwt_pair_for_user(user)
            response = {"message": "Log in Success!", "tokens": tokens}
            return Response(data=response, status=status.HTTP_200_OK)
        else:
            return Response(data={"message": "Invalid email or password"})

    @swagger_auto_schema(
        operation_summary="Get request info",
        operation_description="Get info about logged in user"
    )
    def get(self, request: Request):
        content = {"user": str(request.user), "auth": str(request.auth)}

        return Response(data=content, status=status.HTTP_200_OK)


""" class LoginView(generics.GenericAPIView):
    #created to enable swagger parameter field
    serializer_class = LogInSerializer
    permission_classes = []
    @swagger_auto_schema(
        operation_summary="Log user in with email and password",
        operation_description="Log user in with email and password"
    )
    def post(self, request: Request):
        data = request.data
        email = request.data.get("email")
        password = request.data.get("password")

        #code strats
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save()
            data = serializer.data
        user = authenticate(email=email, password = password)
        if user is not None:
            tokens = create_jwt_pair_for_user(user)
            response = {"message": "Log in Success!", "tokens": tokens, "data": data}
            return Response(data=response, status=status.HTTP_200_OK)
        else:
            return Response(data={"message": "Invalid email or password"})

    @swagger_auto_schema(
        operation_summary="Get request info",
        operation_description="Get info about logged in user"
    )
    def get(self, request: Request):
        content = {"user": str(request.user), "auth": str(request.auth)}

        return Response(data=content, status=status.HTTP_200_OK) """



""" class NoteListView(generics.GenericAPIView, mixins.ListModelMixin, mixins.CreateModelMixin):
    
    #a view for creating and listing Notes
    
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Note.objects.all()

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(author=user)
        return super().perform_create(serializer)

    def get(self, request: Request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request: Request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

class NoteRetrieveUpdateDeleteView(
    generics.GenericAPIView,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    serializer_class = NoteSerializer
    queryset = Note.objects.all()
    permission_classes = [AuthorOrReadOnly]

    def get(self, request: Request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request: Request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request: Request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)



class ListNotesForAuthor(generics.GenericAPIView, mixins.ListModelMixin):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        username = self.request.query_params.get("username") or None

        queryset = Note.objects.all()

        if username is not None:
            return Note.objects.filter(author__username=username)

        return queryset

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs) 







if user is not None:
    tokens = create_jwt_pair_for_user(user)

def filterNotes(request, *pk):
    filter notes by tag
    tag_list = [Tag.objects.get(id=id) for id in pk]
    #filter_tag = Tag.objects.get(id=pk)
    user = request.user
    notes = user.user.notes.all()
    filtered_notes = []
    for tag in tag_list:
        for note in notes:
            if note not in filtered_notes:
                if tag in note.tags.all():
                    filtered_notes.append(note)
    #notes = user.user_notes.filter(tags = filter_tag)
    if len(filtered_notes) > 0:
        serializer = NoteSerializer(filtered_notes, many=True)
        return Response(serializer.data)
    else:
        return Response("Invalid Tag")"""