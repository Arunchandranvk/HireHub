from django.urls import path
from .views import *


urlpatterns = [
    path('comany-home/',ComanyHome.as_view(),name='ch'),
    path('comany-jobs/',JobPostingView.as_view(),name='job-cmpy')
    
]
