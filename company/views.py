from django.shortcuts import render,redirect,get_object_or_404
from django.views.generic import TemplateView,View
from college_admin.forms import *
from django.contrib import messages

# Create your views here.


class ComanyHome(TemplateView):
    template_name = 'company_home.html'




class JobPostingView(View):
    template_name = 'company-jobs.html'
    
    def get(self, request, *args, **kwargs):
        company = Company.objects.all()
        count = company.count()
        department = Department.objects.all()
        context = {
            'students':Company,
            'department':department,
            'count':count
            
        }
        return render(request, self.template_name, context)
    
class JobPostingAddView(View):
    def post(self, request, *args, **kwargs):
        form = StudentForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Student Added Successfully!")
            return redirect('student')
        else:
            messages.error(request, "Failed. Please correct the errors below!")
            students = Student.objects.all()
            context = {
                'students': students,
                'form': form
            }
            return render(request, self.template_name, context)


class JobsPUTView(View): 
    template_name = 'job_edit.html'
    
    def get(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        company = get_object_or_404(Company, id=id)
        department = Department.objects.all()
        form = CompanyForm(instance=company)
        
        context = {
            'form': form,
            'company': company,
            'department': department
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        com = get_object_or_404(Company, id=id)
        form = CompanyForm(request.POST, request.FILES, instance=com)
        
        if form.is_valid():
            form.save()
            messages.success(request, "Company Updated Successfully!")
            return redirect('job-cmpy')  # Ensure correct URL name
        else:
            messages.error(request, "Failed. Please correct the errors below!")
            department = Department.objects.all()
            context = {
                'form': form,
                'company': com,
                'department': department
            }
            return render(request, self.template_name, context)
        
def JobDeleteView(req,pk):
    com = Company.objects.get(id=pk)
    com.delete()
    return redirect('job-cmpy')