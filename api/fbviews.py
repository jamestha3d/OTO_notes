from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

notes = [
    {
        "id": 1,
        "title": "first note",
        "body": "first note body. yipee"
    },
    {
        "id": 2,
        "title": "second note",
        "body": "second note body. yipe"
    },
    {
        "id": 3,
        "title": "third note",
        "body": "third note body. yipe"
    },
]


@api_view(http_method_names=["GET", "POST"])
def homepage(request: Request):

    if request.method == "POST":
        data = request.data

        response = {"message": "Hello", "data": data}
        return Response(data=response, status=status.HTTP_200_OK)
    response = {
        "message": "Hello world"
    }
    return Response(data=response, status=status.HTTP_200_OK)


@api_view(http_method_names=["GET"])
def list_notes(request: Request):
    return Response(data=notes, status=status.HTTP_200_OK)


@api_view(http_method_names=["GET"])
def note_detail(request: Request, note_index: int):
    note = notes[note_index]

    if note:
        return Response(data=note, status=status.HTTP_200_OK)

    return Response(data={"error": "Note not found"}, status=status.HTTP_404_NOT_FOUND)
