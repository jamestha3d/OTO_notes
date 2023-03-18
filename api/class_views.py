from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
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

class NoteListCreateView(APIView):
    """
        View for creating and listing Notes
    """
    serializer_class = NoteSerializer
    def get(self, request:Request, *args, **kwargs):
        notes = Note.objects.all()
        serializer = self.serializer_class(instance=notes, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
        
    def post(self, request:Request, *args, **kwargs):
        data = request.data
        serializer = self.serializer_class(data=data)
        
        if serializer.is_valid():
            serializer.save()
            response = {
                "message": "Note Created",
                "data": serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class NoteRetrieveUpdateDeleteView(APIView):
    serializer_class = NoteSerializer

    def get(self, request:Request, note_id:int):
        note = get_object_or_404(Note, pk=note_id)
        serializer = self.serializer_class(instance=note)

        return Response(data=serializer.data, status=status.HTTP_200_OK)
        pass

    def put(self, request:Request, note_id:int):
        note = get_object_or_404(Note, pk=note_id)
        data = request.data
        serializer =self.serializer_class(instance=note, data=data)
        if serializer.is_valid():
            serializer.save()
            response = {
                "message": "Note updated",
                "data": serializer.data
            }
            return Response(data=response, status = status.HTTP_200_OK)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request:Request, note_id:int):
        note = get_object_or_404(Note, pk=note_id)
        note.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        pass
        