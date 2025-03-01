from django.urls import path
from .views import *


urlpatterns = [
    path('comany-home/',ComanyHome.as_view(),name='ch'),
    path('jobs/', job_list, name='job_list'),
    path('jobs/add/',add_job, name='add_job'),
    path('jobs/edit/<int:job_id>/', edit_job, name='edit_job'),
    path('jobs/delete/<int:job_id>/', delete_job, name='delete_job'),
    path('jobs/applications/<int:job_id>/', view_applications, name='view_applications'),
    path('applications/update/<int:application_id>/', update_application_status, name='update_application_status'),
    path('company/candidates-latest/', CompanyCandidatesView.as_view(), name='company-candidates'),
    path('company/candidates/<int:pk>/', CandidateDetailView.as_view(), name='candidate-detail'),
    path('company/candidates/<int:application_id>/schedule-interview/', ScheduleTechInterviewView.as_view(), name='schedule-interview'),
    path('resend-interview-notification/<int:pk>/', resend_interview_notification, name='resend-interview-notification'),
]
