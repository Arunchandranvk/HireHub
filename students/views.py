from django.shortcuts import render,get_object_or_404,redirect
from django.views.generic import TemplateView,View
from college_admin.models import *
from .forms import *
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
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
            update_session_auth_hash(request, user)  # Prevents logout after password change
            messages.success(request, "Your password has been changed successfully!")
            return redirect("profile")  # Redirect to the user's profile or another page
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PasswordChangeForm(user=request.user)
    
    return render(request, "change_password.html", {"form": form})

class JobsView(TemplateView):
    template_name = 'student-job.html'
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context ['jobs'] = JobPosts.objects.all()
        return context
    


