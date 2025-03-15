from django.urls import path
from .views import *


urlpatterns = [
    path('',LoginView.as_view(),name='login'),
    path('logout/',custom_logout,name='logout'),
    path('company-register/',CompanyRegView.as_view(),name='com-reg'),
    path('company-view/',CompanyView.as_view(),name='company'),
    path('company-detail-view/<int:pk>/',CompanyDetailView.as_view(),name='company-detail'),
    path('company-approve/<int:pk>/',CompanyApproveView.as_view(),name='company-approve'),
    path('company-revoke/<int:pk>/',CompanyRevokeView.as_view(),name='company-revoke'),
    path('admin-home/',AdminHomeView.as_view(),name='ah'),
    path('add-student/',AddStudent.as_view(),name='add-stu'),
    path('edit-student/<int:pk>/',StudentPUTView.as_view(),name='edit-stu'),
    path('del-student/<int:pk>/',StudentDeleteView,name='del-stu'),
    path('students/',StudentView.as_view(),name='stu'),
    path('department/',DepartmentView.as_view(),name='department'),
    path('department/edit/<int:pk>/', DepartmentUpdateView, name='edit-department'),
    path('department/delete/<int:pk>/', DepartmentDeleteView, name='delete-department'),
    path('jobs-lists/<int:pk>/', JobListingsView.as_view(), name='jobs'),
    path('Appliedstudents-lists/<int:pk>/', AppliedStudentsView.as_view(), name='stu-list'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/<str:token>/', ResetPasswordView.as_view(), name='reset-password'),
]
