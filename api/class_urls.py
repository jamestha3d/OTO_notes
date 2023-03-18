from .import class_views
from django.urls import path

urlpatterns = [
    path("homepage/", class_views.homepage, name="notes_home"),
    path("", class_views.NoteListCreateView.as_view(), name="list_notes"),
    path("<int:pk>/", class_views.NoteRetrieveUpdateDeleteView.as_view(), name="post_detail",)
]