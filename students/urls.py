from django.urls import path
from .views import *

urlpatterns = [
    path('student-home/',StudentHome.as_view(),name='sh'),
    path('student-profile/',ProfileView.as_view(),name='profile'),
    path('student-profile/edit/<int:pk>/',ProfilePUTView.as_view(),name='profile-edit'),
    path('change-password/',ChangePasswordView,name='change-password'),
    path('student-jobs/',JobsView.as_view(),name='jobposts'),
]
