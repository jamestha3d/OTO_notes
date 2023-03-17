from django.urls import path, include, re_path
from . import views


from rest_framework_simplejwt.views import (
    
    TokenObtainPairView, TokenRefreshView, TokenVerifyView
)

urlpatterns = [
    path('index/', views.index, name="index"),
    path('notes/', views.getNotes, name="getNotes"),
    path('note/<int:pk>/', views.getNote, name="getNote"),
    path('add/', views.addNote, name="addNote"),
    path('update/<int:pk>/', views.updateNote),
    path('delete/<int:pk>/', views.deleteNote),
    path('filter/<str:pk>/', views.filterNotes),
    path('search/<str:keyword>/', views.search),

    path('authenticate/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view()),
    path('signup/', views.SignUpView.as_view(), name='signUp'),
    path('login/', views.LoginView.as_view(), name="login"),
    path('all_notes/', views.getPublicNotes, name="publicNotes")
    
    
]


