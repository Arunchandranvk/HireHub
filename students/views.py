from django.shortcuts import render,get_object_or_404,redirect
from django.views.generic import TemplateView,View,CreateView,ListView,DetailView
from college_admin.models import *
from .forms import *
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
import random
# Create your views here.


class StudentHome(TemplateView):
    template_name = 'student_home.html'

class ProfileView(View):
    template_name = 'profile.html'
    def get(self, request, *args, **kwargs):
        print(request.user)
        user = CustomUser.objects.get(id=request.user.id)
        student = Student.objects.get(id=user.id)
        context = {
            'user':student
            
        }
        return render(request, self.template_name, context)
    


class ProfilePUTView(View): 
    template_name = 'profile_edit.html'
    
    def get(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        student = get_object_or_404(Student, id=id)
        form = StudentForm(instance=student)
        dep = Department.objects.all()
        context = {
            'form': form,
            'user': student,
            'department':dep
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        stu = get_object_or_404(Student, id=id)
        form = ProfileForm(request.POST, request.FILES, instance=stu)
        print(form)
        if form.is_valid():
            form.save()
            messages.success(request, "Student Updated Successfully!")
            return redirect('profile')  
        else:
            messages.error(request, "Failed. Please correct the errors below!")
            department = Department.objects.all()
            context = {
                'form': form,
                'student': stu,
                'department': department
            }
            return render(request, self.template_name, context)
        
    
@login_required
def ChangePasswordView(request):
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  
            messages.success(request, "Your password has been changed successfully!")
            return redirect("profile")  
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PasswordChangeForm(user=request.user)
    
    return render(request, "change_password.html", {"form": form})

class JobsView(TemplateView):
    template_name = 'student-job.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['jobs'] = JobPosts.objects.all()
        return context

import os

class ApplyJobView(LoginRequiredMixin, CreateView):
    model = AppliedStudents
    template_name = 'apply-job.html'
    fields = ['cv']
    success_url = reverse_lazy('applied-jobs')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        job_id = self.kwargs.get('job_id')
        context['jobpost'] = get_object_or_404(JobPosts, id=job_id)
        return context

    def form_valid(self, form):
        job_id = self.kwargs.get('job_id')
        job = get_object_or_404(JobPosts, id=job_id)
        student = Student.objects.get(id=self.request.user.id)

        # Check if the student has already applied
        if AppliedStudents.objects.filter(student=student, jobpost=job).exists():
            messages.error(self.request, "You have already applied for this job.")
            return redirect('jobposts')

        # Validate the uploaded file (must be PDF and ≤5MB)
        cv_file = self.request.FILES.get('cv')
        if cv_file:
            ext = os.path.splitext(cv_file.name)[1].lower()
            if ext != '.pdf':
                messages.error(self.request, "Only PDF files are allowed.")
                return redirect('apply-job', job_id=job_id)
            if cv_file.size > 5 * 1024 * 1024:  # 5MB limit
                messages.error(self.request, "File size must be less than 5MB.")
                return redirect('apply-job', job_id=job_id)

        # Assign the student and jobpost to the application
        form.instance.student = student
        form.instance.jobpost = job
        messages.success(self.request, "Successfully applied for the job.")
        return super().form_valid(form)

class AppliedJobsView(LoginRequiredMixin, ListView):
    model = AppliedStudents
    template_name = 'applied-jobs.html'
    context_object_name = 'applications'
    
    def get_queryset(self):
        student = Student.objects.get(id=self.request.user.id)
        return AppliedStudents.objects.filter(student=student).order_by('-created_at')

class ApprovedCompaniesView(ListView):
    model = Company
    template_name = 'companies.html'
    context_object_name = 'companies'
    
    def get_queryset(self):
        return Company.objects.filter(status='Approved')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class CompanyDetailView(DetailView):
    model = Company
    template_name = 'company-detail.html'
    context_object_name = 'company'
    
    def get_queryset(self):
        # Only show approved companies
        return Company.objects.filter(status='Approved')
    
from django.utils import timezone
    
@login_required
def student_applications(request):
    student = get_object_or_404(Student, id=request.user.id)
    applications = AppliedStudents.objects.filter(student=student).order_by('-id')
    
    now = timezone.now()
    seven_days_later = now + timezone.timedelta(days=7)
    
    upcoming_interviews = TechInterview.objects.filter(
        applied__student=student,
        start_time__gte=now,
        start_time__lte=seven_days_later
    ).order_by('start_time')
    
    # Get notifications
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:10]
    unread_notifications = [n for n in notifications if not n.is_read]
    
    context = {
        'applications': applications,
        'upcoming_interviews': upcoming_interviews,
        'notifications': notifications,
        'unread_notifications': unread_notifications,
    }
    return render(request, 'notifications.html', context)

@login_required
def mark_all_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect('student-applications')




@login_required
def start_mock_test(request, subject_id):
    subject = Subject.objects.get(id=subject_id)
    
    questions = list(Question.objects.filter(subject=subject).annotate(
        option_count=Count('options')
    ).filter(option_count__gt=1))
    
    if len(questions) < 15:
        return render(request, 'error.html', {'message': 'Not enough questions available'})
    
    # Randomly select 15 unique questions
    selected_questions = random.sample(questions, 15)
    
    # Create mock test
    mock_test = MockTest.objects.create(
        user=request.user,
        subject=subject,
        total_questions=15
    )
    
    # Prepare context with questions and their options
    context = {
        'mock_test': mock_test,
        'questions': [
            {
                'id': q.id,
                'text': q.text,
                'options': list(q.options.all().order_by('?'))
            } for q in selected_questions
        ]
    }
    
    return render(request, 'mock_test.html', context)

@login_required
def submit_mock_test(request, mock_test_id):
    if request.method == 'POST':
        mock_test = MockTest.objects.get(id=mock_test_id)
        
        correct_answers = 0
        total_questions = 0
        
        for key, selected_option_id in request.POST.items():
            if key.startswith('question_'):
                question_id = key.split('_')[1]
                
                try:
                    question = Question.objects.get(id=question_id)
                    selected_option = Option.objects.get(id=selected_option_id)
                    
                    # Create response
                    response = MockTestResponse.objects.create(
                        mock_test=mock_test,
                        question=question,
                        selected_option=selected_option,
                        is_correct=selected_option.is_correct
                    )
                    
                    total_questions += 1
                    if selected_option.is_correct:
                        correct_answers += 1
                except:
                    continue
        
        # Calculate score
        score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        
        # Update mock test
        mock_test.end_time = timezone.now()
        mock_test.score = score
        mock_test.save()
        
        return render(request, 'mock_test_result.html', {
            'mock_test': mock_test,
            'correct_answers': correct_answers,
            'total_questions': total_questions,
            'score': score
        })
    
    return redirect('mock_test_list')

@login_required
def mock_test_list(request):
    subjects = Subject.objects.annotate(
        question_count=Count('question')
    ).filter(question_count__gte=15)
    
    mock_tests = MockTest.objects.filter(user=request.user).order_by('-start_time')
    
    return render(request, 'mock_test_list.html', {
        'subjects': subjects,
        'mock_tests': mock_tests
    })
    
    
from .groq_assessment import *
from .audio_video import *
from .answer_recorder import *
from college_admin.forms import *

class AssessmentHomeView(LoginRequiredMixin, View):
    def get(self, request):
        """Display the assessment configuration page"""
        form = AssessmentConfigForm()
        return render(request, 'start.html', {
            'form': form
        })

    def post(self, request):
        """Process assessment configuration and start session"""
        form = AssessmentConfigForm(request.POST)
        if form.is_valid():
            num_questions = form.cleaned_data['num_questions']
            
            # Create a new assessment session
            session = AssessmentSession.objects.create(
                student=request.user,
                total_questions=num_questions
            )
            
            # Redirect to first question
            return redirect('question', session_id=session.id, question_number=1)
        
        return render(request, 'start.html', {
            'form': form
        })

class QuestionView(LoginRequiredMixin, View):
    def get(self, request, session_id, question_number):
        """Display a specific question for the assessment"""
        try:
            session = AssessmentSession.objects.get(id=session_id, student=request.user)
            
            # Generate question using Groq Assessment logic
            groq_assessment = GroqAssessment()
            question, model_answer = groq_assessment.generate_question()
            
            # Save the current question in the session
            session.current_question = question
            session.current_model_answer = model_answer
            session.save()
            
            return render(request, 'question.html', {
                'session': session,
                'question': question,
                'question_number': question_number,
                'total_questions': session.total_questions
            })
        except AssessmentSession.DoesNotExist:
            messages.error(request, "Invalid assessment session.")
            return redirect('start_assessment')

import base64
import os

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

class SubmitAnswerView(LoginRequiredMixin, View):
    def post(self, request, session_id, question_number):
        try:
            session = AssessmentSession.objects.get(id=session_id, student=request.user)
            
            # Handle video upload
            video_data = request.POST.get('video_data', '')
            student_answer = request.POST.get('student_answer', '')
            print("=====",video_data)
            print("---",student_answer)
          
            if video_data:
                if video_data.startswith('data:video/webm;base64,'):
                    video_data = video_data.split(',')[1]
                
                # Decode base64 to file
                video_content = base64.b64decode(video_data)
                
                # Generate unique filename
                filename = f"{request.user.name}_q{question_number}_{session_id}.webm"
                file_path = os.path.join('assessment_videos', filename)
                
                # Save file
                saved_path = default_storage.save(file_path, ContentFile(video_content))
            else:
                saved_path = None
            
            # Evaluate answer using Groq Assessment
            groq_assessment = GroqAssessment()
            marks, feedback = groq_assessment.evaluate_answer(
                session.current_model_answer, 
                student_answer
            )
            
            # Save student's answer
            StudentAnswer.objects.create(
                session=session,
                question=session.current_question,
                student_answer=student_answer,
                model_answer=session.current_model_answer,
                marks=marks,
                feedback=feedback,
                video_file=saved_path  # Optional: save video file path
            )
            
            # Move to next question or finish assessment
            if question_number < session.total_questions:
                return redirect('question', 
                                session_id=session_id, 
                                question_number=question_number+1)
            else:
                return redirect('results', session_id=session_id)
        
        except AssessmentSession.DoesNotExist:
            messages.error(request, "Invalid assessment session.")
            return redirect('start')
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('start')

class AssessmentResultsView(LoginRequiredMixin, View):
    def get(self, request, session_id):
        """Display assessment results"""
        try:
            session = AssessmentSession.objects.get(id=session_id, student=request.user)
            answers = StudentAnswer.objects.filter(session=session)
            
            total_marks = sum(answer.marks for answer in answers)
            average_score = total_marks / len(answers) if answers else 0
            
            return render(request, 'results.html', {
                'session': session,
                'answers': answers,
                'total_marks': total_marks,
                'average_score': average_score
            })
        except AssessmentSession.DoesNotExist:
            messages.error(request, "Invalid assessment session.")
            return redirect('start_assessment')
        
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Avg

@login_required
def assessment_history(request):
    """
    Display the user's assessment history with pagination and filtering
    """
    # Retrieve all assessment sessions for the logged-in user
    sessions_list = AssessmentSession.objects.filter(
        student=request.user
    ).order_by('-created_at')

    # Prepare additional context for each session
    for session in sessions_list:
        # Get all answers for this session
        session_answers = StudentAnswer.objects.filter(session=session)
        
        # Calculate overall session metrics
        session.answers = session_answers
        session.total_questions = session_answers.count()
        
        # Calculate overall score
        session.overall_score = calculate_overall_score(session_answers)
        
        # Calculate session duration (if tracking is implemented)
        session.duration = calculate_session_duration(session)

    # Implement pagination
    page = request.GET.get('page', 1)
    filter_option = request.GET.get('filter', 'all')

    # Additional filtering logic
    if filter_option == 'last_30_days':
        from django.utils import timezone
        import datetime
        thirty_days_ago = timezone.now() - datetime.timedelta(days=30)
        sessions_list = sessions_list.filter(created_at__gte=thirty_days_ago)
    elif filter_option == 'this_year':
        from django.utils import timezone
        current_year = timezone.now().year
        sessions_list = sessions_list.filter(created_at__year=current_year)

    paginator = Paginator(sessions_list, 5)  # 5 sessions per page

    try:
        sessions = paginator.page(page)
    except PageNotAnInteger:
        sessions = paginator.page(1)
    except EmptyPage:
        sessions = paginator.page(paginator.num_pages)

    # Prepare context for template
    context = {
        'assessment_sessions': sessions,
        'total_assessments': sessions_list.count(),
        'average_score': calculate_overall_average_score(sessions_list),
        'current_filter': filter_option,
        'paginator': paginator
    }

    return render(request, 'history.html', context)

def calculate_overall_score(session_answers):
    """
    Calculate the overall score for a session
    """
    if not session_answers:
        return 0
    
    total_marks = sum(answer.marks for answer in session_answers)
    max_possible_marks = len(session_answers) * 100  # Assuming each question is out of 5
    
    return round((total_marks / max_possible_marks) * 100, 2)

def calculate_session_duration(session):
    """
    Calculate the duration of an assessment session
    Note: This requires tracking start and end times
    """
    # Placeholder implementation
    # In a real-world scenario, you'd track actual session start and end times
    return 30  # Default 30 minutes

def calculate_overall_average_score(sessions):
    """
    Calculate the user's overall average score across all assessment sessions
    """
    if not sessions:
        return 0
    
    total_scores = [calculate_overall_score(session.studentanswer_set.all()) for session in sessions]
    return round(sum(total_scores) / len(total_scores), 2)

from django.db import transaction
from django.http import JsonResponse


@login_required
def delete_assessment_session(request, session_id):
    """
    Delete a specific assessment session
    Supports both GET (render modal) and POST (actual deletion)
    """
    try:
        # Fetch the specific session belonging to the current user
        session = get_object_or_404(
            AssessmentSession, 
            id=session_id, 
            student=request.user
        )

        if request.method == 'POST':
            # Use transaction to ensure atomic deletion
            with transaction.atomic():
                # First, delete associated student answers
                StudentAnswer.objects.filter(session=session).delete()
                
                # Then delete the session itself
                session.delete()

                # Add success message
                messages.success(
                    request, 
                    'Assessment session successfully deleted.'
                )

                # Return JSON response for AJAX requests
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Session deleted successfully.'
                    })
                
                # Redirect for non-AJAX requests
                return redirect('assessment_history')

        # For GET request, prepare context for confirmation modal
        return render(request, 'delete_session_modal.html', {
            'session': session
        })

    except Exception as e:
        # Log the error
        print(f"Error deleting session: {e}")
        
        # Handle error response
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'message': 'Failed to delete session.'
            }, status=400)
        
        messages.error(request, 'Failed to delete the assessment session.')
        return redirect('assessment_history')

@login_required
def bulk_delete_sessions(request):
    """
    Bulk delete multiple assessment sessions
    """
    if request.method == 'POST':
        # Get list of session IDs to delete
        session_ids = request.POST.getlist('session_ids')
        
        try:
            with transaction.atomic():
                # Ensure sessions belong to current user
                sessions = AssessmentSession.objects.filter(
                    id__in=session_ids, 
                    student=request.user
                )
                
                # Delete associated answers first
                StudentAnswer.objects.filter(session__in=sessions).delete()
                
                # Delete sessions
                deleted_count = sessions.count()
                sessions.delete()
                
                messages.success(
                    request, 
                    f'{deleted_count} assessment sessions deleted successfully.'
                )
                
                return redirect('assessment_history')
        
        except Exception as e:
            print(f"Bulk delete error: {e}")
            messages.error(request, 'Failed to delete selected sessions.')
            return redirect('assessment_history')
    
    # If not a POST request
    messages.error(request, 'Invalid request method.')
    return redirect('assessment_history')