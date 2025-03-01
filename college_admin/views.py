from django.shortcuts import render,redirect,get_object_or_404
from django.views.generic import TemplateView,FormView,CreateView,UpdateView,DeleteView,View
from django.http import JsonResponse
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import authenticate,login,logout
from .forms import *
from .models import *
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count
from django.db.models import Q


def custom_logout(request):
    auth_logout(request)
    return redirect('login')

class AdminHomeView(TemplateView):
    template_name='admin_home.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stu']= Student.objects.first()
        context['com']=Company.objects.first()
        context['dep']=Department.objects.first()
        return context

class StudentView(TemplateView):
    template_name='students.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['students'] = Student.objects.all()
        context['department'] = Department.objects.all()
        return context


class AddStudent(CreateView):
    template_name = 'student_add.html'
    model = Student 
    form_class = StudentForm 
    success_url = reverse_lazy('stu')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['department'] = Department.objects.all()
        return context

class StudentPUTView(View): 
    template_name = 'student_edit.html'
    def get(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        student = get_object_or_404(Student, id=id)
        department = Department.objects.all()
        form = StudentForm(instance=student)
        
        context = {
            'form': form,
            'student': student,
            'department': department
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        stu = get_object_or_404(Student, id=id)
        form = StudentForm(request.POST, request.FILES, instance=stu)
        
        if form.is_valid():
            form.save()
            messages.success(request, "Student Updated Successfully!")
            return redirect('stu')  # Ensure correct URL name
        else:
            messages.error(request, "Failed. Please correct the errors below!")
            department = Department.objects.all()
            context = {
                'form': form,
                'student': stu,
                'department': department
            }
            return render(request, self.template_name, context)
        
def StudentDeleteView(req,pk):
    stu = Student.objects.get(id=pk)
    stu.delete()
    return redirect('stu')


class CompanyRegView(SuccessMessageMixin,CreateView):
     form_class= CompanyForm 
     template_name="reg.html" 
     model=Company 
     success_url=reverse_lazy("login")  
     success_message="Registration Successful!!"

     def form_invalid(self, form):
         messages.error(self.request,"Registration failed. Please correct the errors below!")
         return super().form_invalid(form)




class LoginView(FormView):
    template_name = "login.html"
    form_class = LogForm

    def post(self, request, *args, **kwargs):
        form = LogForm(data=request.POST)
        if form.is_valid():  
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            
            user = authenticate(request, email=email, password=password)
            print("user",user)
            if user:
                login(request, user)

                if request.user.is_superuser:
                    return redirect('ah')
                elif not request.user.is_company:
                    return redirect('sh')
                elif request.user.company.status == "Approved":
                        return redirect('ch')
                else:
                    messages.error(request, "No Permission is granted. Please stay tuned!!")
                    return redirect('login')
            else:
                messages.error(request, "Invalid email or password.")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")

        return render(request, 'login.html', {"form": form})

        


class DepartmentView(View):
    template_name = 'departments.html'
    
    def get(self, request, *args, **kwargs):
        departments = Department.objects.annotate(
            total_students=Count('student')
        ).order_by('name')
        paginator = Paginator(departments, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {
            'departments': page_obj,
            'total_departments': departments.count(),
            'form': DepartmentForm()  
        }
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Department Added Successfully!")
            return redirect('department')
        else:
            messages.error(request, "Failed. Please correct the errors below!")
            departments = Department.objects.annotate(
                total_students=Count('student')
            ).order_by('name')
            context = {
                'departments': departments,
                'total_departments': departments.count(),
                'form': form
            }
            return render(request, self.template_name, context)
        

def DepartmentUpdateView(request, pk):
    dep = get_object_or_404(Department, id=pk)

    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=dep)
        if form.is_valid():
            form.save()
            return redirect('department')  # Ensure 'department' is a valid URL name
    else:
        form = DepartmentForm(instance=dep)

    return render(request, 'departments.html', {'form': form, 'department': dep})


   

def DepartmentDeleteView(req,pk):
        try:
            department = Department.objects.get(id=pk)
            department.delete()
            # messages.success(req,"Deleted Successfully!!!")
            return redirect('department')
        except Exception as e:
            # messages.error(req, f"Error deleting department: {str(e)}")
            return redirect('department')
        

class CompanyView(View):
    template_name = 'company.html'
    
    def get(self, request):
        search_query = request.GET.get('search', '')
        companies = Company.objects.all().order_by('-created_at')
        
        if search_query:
            companies = companies.filter(
                Q(name__icontains=search_query) |
                Q(contact_person__icontains=search_query) |
                Q(email__icontains=search_query)
            )
        print(search_query)
        paginator = Paginator(companies, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'companies': page_obj,
            'total_companies': companies.count()
        }
        return render(request, self.template_name, context)
    

class CompanyDetailView(View):
    def get(self, request, pk):
        company = get_object_or_404(Company, pk=pk)
        data = {
            'Name': company.name,
            'Location': company.location,
            'Website': company.site_url,
            'Email': company.email,
            'Phone': company.phone
        }
        return JsonResponse(data)



class CompanyApproveView(View):
    def get(self, request, pk):
        company = get_object_or_404(Company, pk=pk)
        company.status = "Approved"
        company.save()
        # messages.success(request, f"{company.name} has been approved!")
        return redirect('company')

class CompanyRevokeView(View):
    def get(self, request, pk):
        company = get_object_or_404(Company, pk=pk)
        company.status = "Revoked"
        company.save()
        # messages.success(request, f"Approval revoked for {company.name}")
        return redirect('company')

class CompanyDeleteView(View):
    def get(self, request, pk):
        company = get_object_or_404(Company, pk=pk)
        company.delete()
        # messages.success(request, "Company deleted successfully!")
        return redirect('company')
    

class JobListingsView(TemplateView):
    template_name = "jobs.html"
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        id=kwargs.get('pk')
        context['jobs'] = JobPosts.objects.filter(company=id)
        return context

class AppliedStudentsView(TemplateView):
    template_name = "applied_students.html"
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        id=kwargs.get('pk')
        context['students'] = AppliedStudents.objects.filter(jobpost=id)
        return context
    
   