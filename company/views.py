from django.shortcuts import render,redirect,get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView,TemplateView
from django.urls import reverse_lazy
from college_admin.forms import *
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.


class ComanyHome(TemplateView):
    template_name = 'company_home.html'


def add_job(request):
    """View for adding a new job post"""
    if request.method == 'POST':
        form = JobPostForm(request.POST)
        if form.is_valid():
            # Create a new job post but don't save yet
            job_post = form.save(commit=False)
            # Assign the current company to the job post
            job_post.company = request.user.company
            # Now save
            job_post.save()
            messages.success(request, "Job post created successfully!")
            return redirect('job_list')
    else:
        form = JobPostForm()
    
    return render(request, 'add_job.html', {'form': form})

def job_list(request):
    """View for listing all job posts with pagination"""
    jobs_list = JobPosts.objects.filter(company=request.user.company).order_by('-opening_date')
    
    # Pagination
    paginator = Paginator(jobs_list, 10)  # Show 10 jobs per page
    page = request.GET.get('page')
    jobs = paginator.get_page(page)
    
    return render(request, 'job_list.html', {'jobs': jobs})

def edit_job(request, job_id):
    """View for editing a job post"""
    job = get_object_or_404(JobPosts, id=job_id, company=request.user.company)
    
    if request.method == 'POST':
        form = JobPostForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "Job post updated successfully!")
            return redirect('job_list')
    else:
        form = JobPostForm(instance=job)
    
    return render(request, 'edit_job.html', {'form': form, 'job': job})

def delete_job(request, job_id):
    """View for deleting a job post"""
    job = get_object_or_404(JobPosts, id=job_id, company=request.user.company)
    
    if request.method == 'POST':
        job.delete()
        messages.success(request, "Job post deleted successfully!")
        return redirect('job_list')
    
    return render(request, 'confirm_delete_job.html', {'job': job})

def view_applications(request, job_id):
    """View for displaying applicants for a specific job"""
    job = get_object_or_404(JobPosts, id=job_id, company=request.user.company)
    applications = AppliedStudents.objects.filter(jobpost=job)
    
    return render(request, 'view_applications.html', {'job': job, 'applications': applications})

def update_application_status(request, application_id):
    """View for updating the status of a job application"""
    application = get_object_or_404(AppliedStudents, id=application_id, jobpost__company=request.user.company)
    
    if request.method == 'POST':
        form = ApplicationStatusForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            messages.success(request, "Application status updated successfully!")
            return redirect('view_applications', job_id=application.jobpost.id)
    else:
        form = ApplicationStatusForm(instance=application)
    
    return render(request, 'update_application_status.html', {
        'form': form, 
        'application': application
    })
    
 
class CompanyCandidatesView(LoginRequiredMixin, ListView):
    model = AppliedStudents
    template_name = 'company-candidates.html'
    context_object_name = 'applications'
    
    def get_queryset(self):
        company = get_object_or_404(Company, id=self.request.user.id)
        # Get all applications for jobs posted by this company
        return AppliedStudents.objects.filter(jobpost__company=company)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = get_object_or_404(Company, id=self.request.user.id)
        context['company'] = company
        context['jobs'] = JobPosts.objects.filter(company=company)
        return context


class CandidateDetailView(LoginRequiredMixin, DetailView):
    model = AppliedStudents
    template_name = 'candidate-detail.html'
    context_object_name = 'application'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        application = self.get_object()
        # Check if this application already has a technical interview scheduled
        try:
            context['tech_interview'] = TechInterview.objects.get(applied=application)
        except TechInterview.DoesNotExist:
            context['tech_interview'] = None
        return context
    
    def get_queryset(self):
        company = get_object_or_404(Company, id=self.request.user.id)
        # Ensure company can only see applications for their own jobs
        return AppliedStudents.objects.filter(jobpost__company=company)
 
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
 
class ScheduleTechInterviewView(LoginRequiredMixin, CreateView):
    model = TechInterview
    form_class = TechInterviewForm  # Use the custom form
    template_name = 'schedule-interview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        application_id = self.kwargs.get('application_id')
        context['application'] = get_object_or_404(AppliedStudents, id=application_id)
        return context

    def form_valid(self, form):
        application_id = self.kwargs.get('application_id')
        application = get_object_or_404(AppliedStudents, id=application_id)

        # Ensure the company owns this job application
        company = get_object_or_404(Company, id=self.request.user.id)
        if application.jobpost.company != company:
            messages.error(self.request, "You don't have permission to schedule an interview for this application.")
            return redirect('company-candidates')

        form.instance.applied = application
        
        interview = form.save()
        formatted_date = interview.start_time.strftime('%B %d, %Y')
        formatted_time = interview.start_time.strftime('%I:%M %p')
        Notification.objects.create(
            user=application.student.user,
            title=f"Technical Interview Scheduled",
            message=f"A technical interview has been scheduled for {application.jobpost.designation} " 
                    f"at {application.jobpost.company.name} on {formatted_date} at {formatted_time}.",
            link=interview.link
        )
        
        # Send email notification to student
        student_email = application.student.email
        job_title = application.jobpost.designation
        company_name = company.name
        
        email_subject = f"Interview Scheduled for {job_title} at {company_name}"
        email_message = f"""
        Dear {application.student.name},
        
        Your technical interview for the position of {job_title} at {company_name} has been scheduled.
        
        Interview Details:
        Date: {formatted_date}
        Time: {formatted_time}
        Link: {interview.link}
        
        Please make sure you're prepared and online a few minutes before the scheduled time.
        
        Best regards,
        {company_name} Recruitment Team
        """
        
        try:
            send_mail(
                email_subject,
                email_message,
                settings.EMAIL_HOST_USER,
                [student_email],
                fail_silently=False,
            )
            messages.success(self.request, "Interview scheduled and notification sent successfully.")
        except Exception as e:
            messages.warning(self.request, f"Interview scheduled but notification email failed to send. Error: {str(e)}")
            
        messages.success(self.request, "Technical interview scheduled successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('candidate-detail', kwargs={'pk': self.kwargs.get('application_id')})


@login_required
def resend_interview_notification(request, pk):
    application = get_object_or_404(AppliedStudents, pk=pk)
    company = get_object_or_404(Company, id=request.user.id)
    
    # Ensure the company owns this job posting
    if application.jobpost.company != company:
        messages.error(request, "You don't have permission to resend this notification.")
        return redirect('company-candidates')
    
    try:
        tech_interview = TechInterview.objects.get(applied=application)
        
        # Create notification record if it doesn't exist
        
        
        # Send email notification to student
        student_email = application.student.email
        job_title = application.jobpost.designation
        company_name = company.name
        interview_date = tech_interview.start_time.strftime("%Y-%m-%d")
        interview_time = tech_interview.start_time.strftime("%H:%M")
        Notification.objects.create(
                user=application.student.user,
                title=f"Technical Interview Reminder",
                message=f"This is a reminder about your upcoming technical interview {application.jobpost.designation} " 
                        f"at {application.jobpost.company.name} on {interview_date} at {interview_time}.",
                
            )
        email_subject = f"Reminder: Interview for {job_title} at {company_name}"
        email_message = f"""
        Dear {application.student.name},
        
        This is a reminder about your upcoming technical interview for the position of {job_title} at {company_name}.
        
        Interview Details:
        Date: {tech_interview.start_time.strftime("%B %d, %Y")}
        Time: {tech_interview.start_time.strftime("%I:%M %p")}
        Link: {tech_interview.link}
        
        Please make sure you're prepared and online a few minutes before the scheduled time.
        
        Best regards,
        {company_name} Recruitment Team
        """
        
        send_mail(
            email_subject,
            email_message,
            settings.EMAIL_HOST_USER,
            [student_email],
            fail_silently=False,
        )
        
        messages.success(request, "Interview notification resent successfully.")
    except TechInterview.DoesNotExist:
        messages.error(request, "No interview scheduled for this candidate.")
    except Exception as e:
        messages.error(request, f"Failed to resend notification. Error: {str(e)}")
    
    return redirect('candidate-detail', pk=pk) 

