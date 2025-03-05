from django.shortcuts import render,redirect,get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView,TemplateView
from django.urls import reverse_lazy
from college_admin.forms import *
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import timedelta
# Create your views here.


class CompanyHome(TemplateView):
    template_name = 'company_home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = self.request.user.company
        now = timezone.now()
        one_week_ago = now - timedelta(days=7)
        
        # Active Jobs Count
        active_jobs = JobPosts.objects.filter(
            company=company,
            closing_date__gte=now.date()
        )
        context['active_jobs_count'] = active_jobs.count()
        
        # Latest closing date
        if active_jobs.exists():
            context['latest_closing_date'] = active_jobs.order_by('closing_date').first().closing_date
        
        # Applications statistics
        applications = AppliedStudents.objects.filter(
            jobpost__company=company
        )
        context['total_applications'] = applications.count()
        context['new_applications'] = applications.filter(
            jobpost__opening_date__gte=one_week_ago.date()
        ).count()
        
        # Recent applications (limit to 5)
        context['recent_applications'] = applications.order_by('-jobpost__opening_date')[:2]
        
        # Interviews data
        interviews = TechInterview.objects.filter(
            applied__jobpost__company=company,
            start_time__gte=now
        ).order_by('start_time')
        
        context['scheduled_interviews_count'] = interviews.count()
        context['upcoming_interviews'] = interviews[:1]  # Limit to 3
        if interviews.exists():
            context['next_interview'] = interviews.first()
        
        # Notifications
        notifications = Notification.objects.filter(user=self.request.user)
        context['notifications'] = notifications[:10]  # Limit to 10 most recent
        context['unread_notifications_count'] = notifications.filter(is_read=False).count()
        
        return context


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
    Notification.objects.create(
            user=application.student,
            title=" Interview Update",
            message=f"Your  interview for {application.jobpost.designation} at {application.jobpost.company.name} "
                    f"Status has been updated",
            # link=interview.link
        )
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
        context['jobs'] = JobPosts.objects.filter(company=company).order_by('-created_at')
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
 
class ScheduleTechInterviewView(LoginRequiredMixin, UpdateView):
    model = TechInterview
    form_class = TechInterviewForm
    template_name = 'schedule-interview.html'

    def get_object(self, queryset=None):
        application_id = self.kwargs.get('application_id')
        application = get_object_or_404(AppliedStudents, id=application_id)
        interview, created = TechInterview.objects.get_or_create(applied=application)
        return interview  # This ensures the form loads existing data if available

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        application_id = self.kwargs.get('application_id')
        context['application'] = get_object_or_404(AppliedStudents, id=application_id)
        return context

    def form_valid(self, form):
        application_id = self.kwargs.get('application_id')
        application = get_object_or_404(AppliedStudents, id=application_id)
        
        # Ensure the logged-in company owns this job application
        company = get_object_or_404(Company, id=self.request.user.id)
        if application.jobpost.company != company:
            messages.error(self.request, "You don't have permission to edit this interview.")
            return redirect('company-candidates')

        form.instance.applied = application  # Ensure the form is linked to the application
        interview = form.save()

        formatted_date = interview.start_time.strftime('%B %d, %Y')
        formatted_time = interview.start_time.strftime('%I:%M %p')

        # Notify the student
        Notification.objects.create(
            user=application.student,
            title="Technical Interview Update",
            message=f"Your technical interview for {application.jobpost.designation} at {application.jobpost.company.name} "
                    f"has been updated. The new schedule is {formatted_date} at {formatted_time}.",
            link=interview.link
        )

        # Send email notification
        
        student_email = application.student.email
        email_subject = f"Updated Interview Schedule for {application.jobpost.designation} at {company.name}"
        email_message = f"""
        Dear {application.student.name},

        Your technical interview for the position of {application.jobpost.designation} at {company.name} has been updated.

        New Interview Details:
        Date: {formatted_date}
        Time: {formatted_time}
        Link: {interview.link}

        Please ensure you're available at the updated time.

        Best regards,
        {company.name} Recruitment Team
        """

        try:
            send_mail(
                email_subject,
                email_message,
                settings.EMAIL_HOST_USER,
                [student_email],
                fail_silently=False,
            )
            messages.success(self.request, "Interview updated and notification sent successfully.")
        except Exception as e:
            messages.warning(self.request, f"Interview updated, but email notification failed: {str(e)}")

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('candidate-detail', kwargs={'pk': self.kwargs.get('application_id')})


@login_required
def edit_technical_interview(request, pk):
    # Get the specific tech interview
    tech_interview = get_object_or_404(TechInterview, pk=pk)
    application = tech_interview.applied
    company = get_object_or_404(Company, id=request.user.id)
    
   
    
    if request.method == 'POST':
        form = TechInterviewForm(request.POST, instance=tech_interview)
        if form.is_valid():
            tech_interview = form.save(commit=False)
            tech_interview.save()
            formatted_date = tech_interview.start_time.strftime('%B %d, %Y')
            formatted_time = tech_interview.start_time.strftime('%I:%M %p')
            # Send email notification to student about rescheduling
            Notification.objects.create(
                user=application.student,
                title="Technical Interview Update",
                message=f"Your technical interview for {application.jobpost.designation} at {application.jobpost.company.name} "
                        f"has been updated. The new schedule is {formatted_date} at {formatted_time}.",
                link=tech_interview.link
            )
            student_email = application.student.email
            job_title = application.jobpost.designation
            company_name = company.name
            
            email_subject = f"Interview Details Updated for {job_title} at {company_name}"
            email_message = f"""
            Dear {application.student.name},
            
            The details for your technical interview for the position of {job_title} at {company_name} have been updated.
            
            Updated Interview Details:
            Date & Time: {tech_interview.start_time.strftime('%Y-%m-%d %H:%M')}
            Link: {tech_interview.link}
            Status: {tech_interview.status}
            
            Please make sure you're prepared and online a few minutes before the scheduled time.
            
            Best regards,
            {company_name} Recruitment Team
            """
            
            try:
                send_mail(
                    email_subject,
                    email_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [student_email],
                    fail_silently=False,
                )
                messages.success(request, "Interview details updated and notification sent successfully.")
            except Exception as e:
                messages.warning(request, f"Interview updated but notification email failed to send. Error: {str(e)}")
            
            return redirect('candidate-detail', pk=application.pk)
    else:
        form = TechInterviewForm(instance=tech_interview)
    
    context = {
        'form': form,
        'application': application,
        'data': {
            'link': tech_interview.link,
            'start_time': tech_interview.start_time,
            'status': tech_interview.status
        }
    }
    
    return render(request, 'edit_technical_interview.html', context)

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


from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncMonth

@login_required
def company_reports(request):
    # Get the current company
    company = request.user.company

    # Total Job Postings
    total_job_postings = JobPosts.objects.filter(company=company).count()
    active_job_postings = JobPosts.objects.filter(
        company=company, 
        closing_date__gte=timezone.now().date()
    ).count()

    # Total Applications
    total_applications = AppliedStudents.objects.filter(
        jobpost__company=company
    ).count()

    # Calculate pass rates
    total_initial_rounds = AppliedStudents.objects.filter(jobpost__company=company).count()
    passed_initial_rounds = AppliedStudents.objects.filter(
        jobpost__company=company, 
        intial_round1='Pass'
    ).count()
    initial_round_pass_rate = round((passed_initial_rounds / total_initial_rounds) * 100, 2) if total_initial_rounds > 0 else 0

    total_tech_rounds = AppliedStudents.objects.filter(jobpost__company=company).count()
    passed_tech_rounds = AppliedStudents.objects.filter(
        jobpost__company=company, 
        tech_round2='Pass'
    ).count()
    tech_round_pass_rate = round((passed_tech_rounds / total_tech_rounds) * 100, 2) if total_tech_rounds > 0 else 0

    # Interviews and Hires
    total_interviews = TechInterview.objects.filter(
        applied__jobpost__company=company
    ).count()
    successful_hires = AppliedStudents.objects.filter(
        jobpost__company=company,
        intial_round1='Pass',
        tech_round2='Pass',
        is_passed=True
    ).count()

    # Calculate overall pass rate
    pass_rate = round((successful_hires / total_applications) * 100, 2) if total_applications > 0 else 0

    # Top Performing Jobs
    top_performing_jobs = JobPosts.objects.filter(company=company).annotate(
        applications_count=Count('job_stuu'),
        hired_count=Count('job_stuu', filter=Q(
            job_stuu__intial_round1='Pass', 
            job_stuu__tech_round2='Pass',
            job_stuu__is_passed=True
        ))
    ).order_by('-applications_count')[:5]

    # Hire Rate
    hire_rate = round((successful_hires / total_applications) * 100, 2) if total_applications > 0 else 0

    # Departments
    departments = Department.objects.all()

    context = {
        'total_job_postings': total_job_postings,
        'active_job_postings': active_job_postings,
        'total_applications': total_applications,
        'pass_rate': pass_rate,
        'total_interviews': total_interviews,
        'successful_hires': successful_hires,
        'top_performing_jobs': top_performing_jobs,
        'initial_round_pass_rate': initial_round_pass_rate,
        'tech_round_pass_rate': tech_round_pass_rate,
        'hire_rate': hire_rate,
        'departments': departments,
        # 'unread_notifications_count': get_unread_notifications_count(request.user)  # Assuming you have this function
    }

    return render(request, 'reports.html', context)

def export_reports_pdf(request):
    """
    Export reports to PDF
    Requires additional libraries like reportlab or xhtml2pdf
    """
    # Implementation for PDF export
    pass

def export_reports_csv(request):
    """
    Export reports to CSV
    Uses Django's built-in CSV response
    """
    import csv
    from django.http import HttpResponse

    # Get the company
    company = request.user.company

    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{company.name}_recruitment_report.csv"'

    # Create a CSV writer
    writer = csv.writer(response)
    
    # Write headers
    writer.writerow([
        'Metric', 'Value'
    ])

    # Write report data
    writer.writerow(['Total Job Postings', JobPosts.objects.filter(company=company).count()])
    writer.writerow(['Active Job Postings', JobPosts.objects.filter(company=company, closing_date__gte=timezone.now().date()).count()])
    writer.writerow(['Total Applications', AppliedStudents.objects.filter(jobpost__company=company).count()])
    
    # More metrics can be added here

    return response

def advanced_analytics(request):
    """
    More advanced analytics and trend analysis
    """
    company = request.user.company

    # Monthly application trends
    monthly_applications = AppliedStudents.objects.filter(
        jobpost__company=company
    ).annotate(
        month=TruncMonth('jobpost__opening_date')
    ).values('month').annotate(
        application_count=Count('id')
    ).order_by('month')

    # Department-wise hiring statistics
    department_hiring = JobPosts.objects.filter(company=company).annotate(
        total_applications=Count('job_stuu'),
        hired_applications=Count('job_stuu', filter=Q(
            job_stuu__intial_round1='Pass', 
            job_stuu__tech_round2='Pass'
        ))
    ).values('department__name', 'total_applications', 'hired_applications')

    context = {
        'monthly_applications': list(monthly_applications),
        'department_hiring': list(department_hiring)
    }

    return render(request, 'advanced_analytics.html', context)