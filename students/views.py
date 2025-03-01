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

class ApplyJobView(LoginRequiredMixin, CreateView):
    model = AppliedStudents
    template_name = 'apply-job.html'
    fields = ['cv']
    success_url = reverse_lazy('applied-jobs')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        job_id = self.kwargs.get('job_id')
        print(job_id)
        context['jobpost'] = get_object_or_404(JobPosts,id=job_id)
        return context
    def form_valid(self, form):
        job_id = self.kwargs.get('job_id')
        job = get_object_or_404(JobPosts, id=job_id)
        student = Student.objects.get(id=self.request.user.id)
        
        if AppliedStudents.objects.filter(student=student, jobpost=job).exists():
            messages.error(self.request, "You have already applied for this job.")
            return redirect('jobposts')
        
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
        return AppliedStudents.objects.filter(student=student)

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