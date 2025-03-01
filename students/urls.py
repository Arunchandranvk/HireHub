from django.urls import path
from .views import *

urlpatterns = [
    path('student-home/',StudentHome.as_view(),name='sh'),
    path('student-profile/',ProfileView.as_view(),name='profile'),
    path('student-profile/edit/<int:pk>/',ProfilePUTView.as_view(),name='profile-edit'),
    path('change-password/',ChangePasswordView,name='change-password'),
    path('student-jobs/',JobsView.as_view(),name='jobposts'),
    path('apply-jobs/<int:job_id>/',ApplyJobView.as_view(),name='apply-job'),
    path('applied-jobs/',AppliedJobsView.as_view(),name='applied-jobs'),
    path('companies/', ApprovedCompaniesView.as_view(), name='companies'),
    path('companies/<int:pk>/', CompanyDetailView.as_view(), name='company-detail'),
    path('student/applications/', student_applications, name='student-applications'),
    path('notifications/mark-all-read/', mark_all_read, name='mark-all-read'),
    
]
