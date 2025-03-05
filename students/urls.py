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
    path('mock-tests/', mock_test_list, name='mock_test_list'),
    path('mock-test/start/<int:subject_id>/', start_mock_test, name='start_mock_test'),
    path('mock-test/submit/<int:mock_test_id>/', submit_mock_test, name='submit_mock_test'),
    path('history/', assessment_history, name='assessment_history'),
    path('start/', AssessmentHomeView.as_view(), name='start_assessment'),
    path('session/<int:session_id>/question/<int:question_number>/', 
         QuestionView.as_view(), name='question'),
    path('session/<int:session_id>/question/<int:question_number>/submit/', 
         SubmitAnswerView.as_view(), name='submit_answer'),
    path('session/<int:session_id>/results/', 
         AssessmentResultsView.as_view(), name='results'),
    path('assessment/history/', assessment_history, name='assessment_history'),
    
    # Delete a single session
    path('assessment/delete_session/<int:session_id>/', 
         delete_assessment_session, 
         name='delete_assessment_session'),
    
    # Bulk delete sessions
    path('assessment/bulk_delete/', 
         bulk_delete_sessions, 
         name='bulk_delete_sessions'),
]
