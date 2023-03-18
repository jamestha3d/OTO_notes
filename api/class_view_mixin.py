from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status, generics, mixins
from rest_framework.decorators import api_view,APIView
from .models import Note
from .serializers import NoteSerializer
from django.shortcuts import get_object_or_404

@api_view(http_method_names=["GET", "POST"])
def homepage(request: Request):
    if request.method == "POST":
        data = request.data
        response = {"message": "Hello world", "data": data}
        return Response(data=response, status=status.HTTP_201_CREATED)
    response = {"message": "Hello World"}
    return Response(data=response, status=status.HTTP_200_OK)

class NoteListCreateView(generics.GenericAPIView, mixins.ListModelMixin, mixins.CreateModelMixin):
    """
        View for creating and listing Notes
    """
    serializer_class = NoteSerializer
    queryset = Note.objects.all()

    def get(self, request:Request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def post(self, request: Request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class NoteRetrieveUpdateDeleteView(generics.GenericAPIView, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    serializer_class = NoteSerializer
    queryset = Note.objects.all()

    def get(self, request:Request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def put(self, request:Request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
    
    def delete(self, request:Request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)